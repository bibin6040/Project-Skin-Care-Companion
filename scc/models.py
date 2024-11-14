from django.db import models

class Registration(models.Model):
    FullName = models.CharField(max_length=100)
    email = models.EmailField()
    DOB = models.DateField(null=True, blank=True)
    password = models.CharField(max_length=20)
    gender = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self) -> str:
        return self.FullName
    
class admin_login(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
   
class PredictionRequest(models.Model):
    user = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name='predictions')
    image = models.ImageField(upload_to='predictions/')
    description = models.TextField()
    duration = models.CharField(max_length=50)
    itchiness = models.CharField(max_length=3)
    pain = models.CharField(max_length=3)
    discharge = models.CharField(max_length=3)
    predicted_disease = models.CharField(max_length=255, blank=True, null=True)
    remedies_and_medicines = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction {self.id} - {self.predicted_disease or 'Pending'}"
    

class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()

    def __str__(self):
        return self.name