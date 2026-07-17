# ==============================================================================
# NOMOGRAMME PRONOSTIQUE - OSTÉOSARCOME (Récidive à 1, 3 et 5 ans)
# Conformité : TRIPOD & REMARK Guidelines
# ==============================================================================

# 1. Installation et chargement des packages requis
# install.packages(c("survival", "rms", "timeROC", "dcurves", "ggplot2"))
library(survival)
library(rms)
library(timeROC)
library(dcurves)
library(ggplot2)

# 2. Préparation des données (Simulation de votre base SPSS nettoyée)
# Assurez-vous que vos variables sont codées en 0 (Non/Bon) et 1 (Oui/Mauvais)
# dataset <- read.csv("votre_base_nette.csv")

# Définition de l'environnement de distribution pour le package rms
dd <- datadist(dataset)
options(datadist = "dd")

# 3. Construction du Modèle de Cox Multivarié (Package rms)
# Le temps doit être en mois (12 = 1 an, 36 = 3 ans, 60 = 5 ans)
cox_model <- cph(Surv(Time_to_Recurrence_months, Recurrence_Event) ~ 
                   Metastasis_at_Diagnosis + 
                   Huvos_Grade_Poor + 
                   Surgical_Margin_R1 + 
                   Tumor_Size_gt8 + 
                   Proximal_Location, 
                 data = dataset, 
                 x = TRUE, y = TRUE, surv = TRUE, time.inc = 12)

# 4. CRÉATION DU NOMOGRAMME
# Définition des fonctions de survie pour 1, 3 et 5 ans
surv_1yr <- function(x) survreg.distributions$exponential$density(x) # Remplacé en interne par cph
surv_1yr <- Survival(cox_model)
S_1 <- function(lp) surv_1yr(12, lp)
S_3 <- function(lp) surv_1yr(36, lp)
S_5 <- function(lp) surv_1yr(60, lp)

nom <- nomogram(cox_model, 
                fun = list(S_1, S_3, S_5), 
                funlabel = c("Probabilité de non-récidive à 1 an", 
                             "Probabilité de non-récidive à 3 ans", 
                             "Probabilité de non-récidive à 5 ans"),
                lp = FALSE, # Masque le Linear Predictor pour plus de clarté
                maxscale = 100)

plot(nom, xfrac = .4) # xfrac ajuste l'espace des labels

# 5. VALIDATION INTERNE (Bootstrap 1000 itérations)
# Calcule le C-index (Indice de Concordance) optimisé
validate_model <- validate(cox_model, method = "boot", B = 1000)
print(validate_model)
# Le C-index corrigé se calcule ainsi : Dxy / 2 + 0.5 (Viser ~0.81 comme dans votre abstract)

# 6. COURBES DE CALIBRATION (Comparaison Prédit vs Observé)
par(mfrow=c(1,3)) # Affiche 3 graphiques côte à côte

# Calibration à 1 an (12 mois)
cal_1 <- calibrate(cox_model, cmethod='KM', method="boot", B=1000, u=12)
plot(cal_1, main="Calibration à 1 an", xlab="Survie Prédite", ylab="Survie Observée (KM)")

# Calibration à 3 ans (36 mois)
cal_3 <- calibrate(cox_model, cmethod='KM', method="boot", B=1000, u=36)
plot(cal_3, main="Calibration à 3 ans", xlab="Survie Prédite", ylab="Survie Observée (KM)")

# Calibration à 5 ans (60 mois)
cal_5 <- calibrate(cox_model, cmethod='KM', method="boot", B=1000, u=60)
plot(cal_5, main="Calibration à 5 ans", xlab="Survie Prédite", ylab="Survie Observée (KM)")

# 7. COURBES ROC DÉPENDANTES DU TEMPS (timeROC)
# Pour démontrer la spécificité et la sensibilité du score dans le temps
ROC_time <- timeROC(T = dataset$Time_to_Recurrence_months,
                    delta = dataset$Recurrence_Event,
                    marker = predict(cox_model),
                    cause = 1,
                    times = c(12, 36, 60),
                    iid = TRUE)

plot(ROC_time, time = 12, col = "red", title = "Courbes ROC dépendantes du temps")
plot(ROC_time, time = 36, col = "blue", add = TRUE)
plot(ROC_time, time = 60, col = "green", add = TRUE)
legend("bottomright", c("1 an", "3 ans", "5 ans"), col = c("red", "blue", "green"), lty = 1)

# 8. ANALYSE DE LA COURBE DE DÉCISION (DCA)
# Indispensable aujourd'hui pour prouver l'utilité clinique du nomogramme
# Calcule le bénéfice net de l'utilisation du nomogramme vs "Traiter tout le monde" ou "Traiter personne"
dataset$Pr_1yr <- 1 - S_1(predict(cox_model)) # Risque de récidive à 1 an

dca_1yr <- dca(Surv(Time_to_Recurrence_months, Recurrence_Event) ~ Pr_1yr, 
               data = dataset, 
               time = 12,
               thresholds = seq(0.01, 0.80, by = 0.01))

plot(dca_1yr) + 
  ggtitle("Decision Curve Analysis (1 an)") +
  theme_minimal()
