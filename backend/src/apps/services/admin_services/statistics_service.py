import logging
from datetime import timedelta
from django.db.models import Count, Q, Sum, Avg, F
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
from src.models import User, Document, AuditLog
from src.apps.interfaces.admin_interfaces.statistics_interface import StatisticsServiceInterface

logger = logging.getLogger(__name__)

class StatisticsService(StatisticsServiceInterface):
    def get_dashboard_stats(self) -> dict:
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        one_year_ago = now - timedelta(days=365)
        today = now.date()  

        # 1. Démographie
        total_citoyens = User.objects.filter(role=User.Role.CITOYEN).count()
        pending_documents = Document.objects.filter(statut=Document.Statut.EN_ATTENTE).count()
        total_citoyens_mois = User.objects.filter(date_joined__gte=thirty_days_ago).count()
        today_validations = Document.objects.filter(
            statut=Document.Statut.VALIDE,
            date_validation__date=today
        ).count()
        active_agents = User.objects.filter(role=User.Role.AGENT, is_active=True).count()
        admin_count = User.objects.filter(role=User.Role.ADMIN, is_active=True).count()
        
        sexe_repartition = User.objects.values('sexe').annotate(count=Count('id'))

        # 2. Répartition par âge (catégories : 0-18, 19-35, 36-60, 60+)
        today = timezone.now().date()
        age_categories = {
            '0-18': 0,
            '19-35': 0,
            '36-60': 0,
            '60+': 0
        }
        # Calcul via date_naissance
        for user in User.objects.filter(date_naissance__isnull=False):
            age = today.year - user.date_naissance.year - ((today.month, today.day) < (user.date_naissance.month, user.date_naissance.day))
            if age <= 18:
                age_categories['0-18'] += 1
            elif age <= 35:
                age_categories['19-35'] += 1
            elif age <= 60:
                age_categories['36-60'] += 1
            else:
                age_categories['60+'] += 1

        # 3. Top 5 provinces (via le lieu_origine -> SecteurChefferie -> Territoire -> Province)
        # On utilise select_related pour éviter trop de requêtes
        from src.models import SecteurChefferie
        top_provinces = (
            User.objects
            .filter(lieu_origine__isnull=False)
            .values('lieu_origine__territoire__province__nom')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )

        # 4. Enrôlements par jour (30 derniers jours)
        enrollments_by_day = (
            User.objects
            .filter(date_joined__gte=thirty_days_ago)
            .annotate(day=TruncDay('date_joined'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )

        # 5. Documents par statut
        doc_status = Document.objects.values('statut').annotate(count=Count('id'))

        # 6. Validations par agent (dernière année)
        validations_by_agent = (
            Document.objects
            .filter(date_validation__gte=one_year_ago, valide_par__isnull=False)
            .values('valide_par__email')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        # 7. Audit logs : actions récentes (exemple : 10 dernières actions)
        recent_audits = AuditLog.objects.select_related('user').order_by('-created_at')[:10]
        recent_audits_data = [
            {
                'action': log.action,
                'user_email': log.user.email if log.user else None,
                'entity_type': log.entity_type,
                'created_at': log.created_at.isoformat()
            }
            for log in recent_audits
        ]

        return {
            
            'total_citoyens': total_citoyens,
            'pending_documents': pending_documents,
            'today_validations': today_validations,
            'active_agents': active_agents,
            'admin_count': admin_count,
            # autres champs optionnels
            'total_citoyens_30d': 0,
            'total_citoyens_30d': total_citoyens_mois,
            'sexe_repartition': list(sexe_repartition),
            'age_repartition': age_categories,
            'top_provinces': list(top_provinces),
            'enrollments_by_day': [
                {'date': item['day'].isoformat(), 'count': item['count']}
                for item in enrollments_by_day
            ],
            'documents_status': list(doc_status),
            'top_validators': list(validations_by_agent),
            'recent_audits': recent_audits_data,
        }