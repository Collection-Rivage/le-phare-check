// Le Phare Check - Scripts JavaScript

// Vérification du statut de connexion
function checkOnlineStatus() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            console.log('App status:', data.status);
        })
        .catch(error => {
            console.error('Erreur de connexion:', error);
        });
}

// Confirmation avant suppression (pour futures fonctionnalités)
function confirmDelete(message) {
    return confirm(message || 'Êtes-vous sûr de vouloir supprimer cet élément ?');
}

// Auto-dismiss des alertes après 5 secondes
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Validation du formulaire de check
const checkForm = document.querySelector('form[action*="check"]');
if (checkForm) {
    checkForm.addEventListener('submit', function(e) {
        const problemeCritique = document.getElementById('probleme_critique');
        
        if (problemeCritique && problemeCritique.checked) {
            if (!confirm('⚠️ Vous avez signalé un problème critique. Un email sera envoyé. Confirmer ?')) {
                e.preventDefault();
            }
        }
    });
}

// Statistiques temps réel (optionnel - pour futures améliorations)
function updateDashboardStats() {
    // Placeholder pour mise à jour temps réel des statistiques
    console.log('Dashboard stats updated');
}

// Gestion des switchs de la checklist
const checkboxes = document.querySelectorAll('.form-check-input[type="checkbox"]');
checkboxes.forEach(function(checkbox) {
    checkbox.addEventListener('change', function() {
        if (!this.checked && this.id !== 'probleme_critique') {
            // Optionnel : ajouter une classe visuelle pour les éléments non-OK
            this.closest('.form-check').classList.add('text-warning');
        } else {
            this.closest('.form-check').classList.remove('text-warning');
        }
    });
});

// Log de démarrage
console.log('✅ Le Phare Check - Application chargée');
checkOnlineStatus();
