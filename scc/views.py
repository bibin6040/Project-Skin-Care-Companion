from django.shortcuts import render,redirect
from .models import *
from django.contrib import messages
from django.http import HttpResponse
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from sklearn.feature_extraction.text import TfidfVectorizer
from django.conf import settings
import pandas as pd
from PIL import Image
import pickle
import numpy as np
import os
from xhtml2pdf import pisa
from django.template.loader import get_template

def index(request):
    if 'user' in request.session:
        return render(request, 'index.html')
    elif 'admin' in request.session:
        return render(request, 'index.html')
    else:
        return redirect(login)
    
def registration(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        date_of_birth = request.POST.get('dob')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmpassword')
        gender = request.POST.get('gender')

        # Basic validation
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect(registration)

        # Create a new Registration object and save it to the database
        registration = Registration.objects.create(
            FullName=fullname,
            email=email,
            DOB=date_of_birth,
            password=password,
            gender=gender
        )
        registration.save()

        return redirect('log')  # Redirect to a login page after registration
    else:
        return render(request, 'Registration.html')
    
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = Registration.objects.get(email=email)
            # Check the hashed password
            if password == user.password:
                request.session['user'] = user.id  # Set session with user ID
                return redirect(userdash)  # Redirect to user dashboard
            else:
                messages.error(request, "Invalid password")
                return redirect(login)
        except Registration.DoesNotExist:
            messages.error(request, "Invalid Email/User does not exist")
            return redirect(login)
    else:
        return render(request, 'Login.html')

def userdash(request):
    if 'user' in request.session:
        return render(request, 'user_dashboard.html')
    return redirect(login)
    

def logout(request):
   if 'user' in request.session:
        del request.session['user']
   return redirect(login)
    
def contact(request):
    return render(request, 'contact.html')

def privacy(request):
    return render(request, 'privacy.html')

def admi(request):
    if request.method == 'POST':
        # Get the username and password from the form
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate the user
        try:
            user = admin_login.objects.get(email=email)
            # Check the hashed password
            if password == user.password:
                request.session['admin_user'] = user.id  # Set session with user ID
                return redirect(admindash)  # Redirect to admin dashboard
            else:
                messages.error(request, "Invalid password")
                return redirect(admi)
        except admin_login.DoesNotExist:
            messages.error(request, "Invalid Email/admin does not exist")
            return redirect(admi)
    else:
        return render(request, 'admin.html')
   

def admindash(request):
    admin_user_id = request.session.get('admin_user')
    
    if admin_user_id:
        admin_user = admin_login.objects.get(id=admin_user_id)
        context = {
            'admin_user': admin_user,
            # Add other context data if needed
        }
        return render(request, 'admin_dashboard.html', context)
    else:
        return redirect('admi')  # Redirect to admin login if no session is found
    


def profile(request):
    if 'user' in request.session:

    #Retrieve the current user's profile
        user_profile = Registration.objects.get(id=request.session['user'])
        
        #Pass the profile data to the template
        context = {
            'profile': user_profile,
        }
        
        return render(request, 'userprofile.html', context)

    return redirect(login)

# Create your views here.
def user_profiles_list(request):
    if request.user.is_staff:  # Ensure that only admin can access this view
        profiles = Registration.objects.all()
        return render(request, 'userlist.html', {'profiles': profiles})
    else:
        return render(request, 'admin_dashboard.html') 
    
disease_classes = {
    0: 'Acne',
    1: 'Actinic Keratosis Basal Cell Carcinoma',
    2: 'Atopic Dermatitis',
    3: 'cellulitis',
    4: 'impetigo',
    5: 'Bacterial Infection',
    6: 'Eczema',
    7: 'Exanthems',
    8: 'athlete-foot',
    9: 'nail-fungus',
    10: 'ringworm',
    11: 'Herpes HPV',
    12: 'cutaneous-larva-migrans',
    13: 'chickenpox',
    14: 'shingles'
    # Add more mappings as needed
}

disease_remedies = {
    'Acne': 'Medicines: Topical retinoids (apply at night to clean, dry skin), benzoyl peroxide (apply to affected areas once or twice daily), antibiotics (clindamycin, doxycycline – take orally as prescribed, usually once or twice a day). Remedies: Gentle cleansing, avoid picking or squeezing, oil-free moisturizers.',
'Actinic Keratosis Basal Cell Carcinoma': 'Medicines: Fluorouracil (apply topically to lesions as directed, usually once or twice daily for several weeks), imiquimod (apply topically as prescribed, usually 2-5 times a week). Remedies: Sun protection, avoid tanning beds, regular skin checks.',
'Atopic Dermatitis': 'Medicines: Topical corticosteroids (apply thinly to affected areas 1-2 times daily), calcineurin inhibitors (tacrolimus, pimecrolimus – apply to affected areas twice daily). Remedies: Moisturizing lotions (apply after bathing), avoid triggers (allergens, irritants), lukewarm baths.',
'cellulitis': 'Medicines: Antibiotics (penicillin, cephalexin – take orally as prescribed, usually for 5-14 days). Remedies: Elevation of the affected area, cool damp cloths, rest.',
'impetigo': 'Medicines: Topical antibiotics (mupirocin, fusidic acid – apply to affected areas 2-3 times daily). Remedies: Wash affected area, keep skin dry, avoid scratching.',
'Bacterial Infection': 'Medicines: Topical or oral antibiotics (mupirocin – apply topically 2-3 times daily, amoxicillin – take orally as prescribed, usually 1-3 times a day). Remedies: Keep the area clean and dry, good hygiene practices.',
'Eczema': 'Medicines: Topical corticosteroids (apply thinly to affected areas 1-2 times daily), moisturizers (use liberally throughout the day). Remedies: Regular moisturization, avoid harsh soaps and irritants, use emollients after baths.',
'Exanthems': 'Medicines: Depends on the cause (antibiotics for bacterial infections – take as prescribed, antivirals for viral infections – take as prescribed). Remedies: Hydration, rest, cool baths to reduce discomfort.',
'athlete-foot': 'Medicines: Topical antifungals (clotrimazole, miconazole – apply to affected areas 2-3 times daily). Remedies: Keep feet clean and dry, wear breathable footwear, use antifungal powder.',
'nail-fungus': 'Medicines: Oral antifungals (terbinafine – take once daily for 6-12 weeks, itraconazole – take as prescribed, usually for 3-6 months). Remedies: Keep nails trimmed and dry, avoid moist environments, wear breathable shoes.',
'ringworm': 'Medicines: Topical antifungals (clotrimazole, miconazole – apply to affected areas 2-3 times daily). Remedies: Keep skin dry, avoid sharing personal items, wash clothes and bedding regularly.',
'Herpes HPV': 'Medicines: Antiviral drugs (acyclovir, valacyclovir – take orally as prescribed, usually 2-5 times daily during outbreaks). Remedies: Avoid skin-to-skin contact during outbreaks, keep area clean, avoid irritants.',
'cutaneous-larva-migrans': 'Medicines: Albendazole (take orally as prescribed, usually once daily for 3-5 days), ivermectin (take orally as prescribed, usually a single dose). Remedies: Anti-itch creams (apply to reduce itching), wear shoes outdoors, avoid walking barefoot in contaminated areas.',
'chickenpox': 'Medicines: Antihistamines (take orally as needed for itching), antiviral (acyclovir – take orally as prescribed, 5 times daily for 5-7 days). Remedies: Oatmeal baths, calamine lotion, avoid scratching.',
'shingles': 'Medicines: Antivirals (acyclovir, valacyclovir – take orally as prescribed, 3-5 times daily for 7-10 days). Remedies: Cool compresses, pain relievers (such as ibuprofen or acetaminophen), oatmeal baths, rest.'

    
}
    
# Default message for unknown diseases
default_message = "I don't know the correct medicine for this. Please refer to a doctor for proper diagnosis and treatment."


# Create your views here for the prediction form.
def predict(request):
    if 'user' in request.session:
        
         
  # Fetch the user from the session

        if request.method == 'POST':
            image = request.FILES.get('image')
            description = request.POST.get('description')
            duration = request.POST.get('duration')
            itchiness = request.POST.get('itchiness')
            pain = request.POST.get('pain')
            discharge = request.POST.get('discharge')
            
            if not (image and description and duration and itchiness and pain and discharge):
                return HttpResponse("Some form fields are missing.", status=400)
            user_id = request.session['user']
            user = Registration.objects.get(id=user_id)

            # Save data to the database
            prediction_request = PredictionRequest(
                user=user,
                image=image,
                description=description,
                duration=duration,
                itchiness=itchiness,
                pain=pain,
                discharge=discharge
            )
            prediction_request.save()

            # Load your trained model (assumed to be an image-based model)
            model = load_model(os.path.join(settings.BASE_DIR, 'model', 'skin_disease_model.h5'))

            # Process the image
            img = Image.open(image).convert('RGB')
            img = img.resize((224, 224))
            img_array = img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)

            # Make prediction using the model (image only)
            prediction = model.predict(img_array)
            predicted_class_index = np.argmax(prediction, axis=1)[0]

            # Map the class index to the disease name
            predicted_disease_name = disease_classes.get(predicted_class_index, "Unknown Disease")
            # Modify your predict function logic to handle unknown diseases
            remedies_and_medicines = disease_remedies.get(predicted_disease_name, default_message)
            # Update the prediction_request instance with the predicted disease
            prediction_request.predicted_disease = predicted_disease_name
            prediction_request.remedies_and_medicines = remedies_and_medicines
            prediction_request.save()  # Save the updated instance

            request.session['predicted_disease'] = predicted_disease_name
            request.session['remedies_and_medicines'] = remedies_and_medicines

            # Redirect to the result page or return the prediction
            return render(request, 'result_page.html', {'prediction': predicted_disease_name,'remedies': remedies_and_medicines})

    return redirect('login')


def contact_view(request):
    if 'user' in request.session:
        if request.method == 'POST':
            name = request.POST.get('name')
            email = request.POST.get('email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')

            # Create and save the Contact object
            contact = Contact(name=name, email=email, subject=subject, message=message)
            contact.save()

            # Optionally, redirect to a success page or back to the form
            return redirect('cont')  # Replace 'success_url' with the URL you want to redirect to

    return redirect(login)

def contact_list(request):
    contacts = Contact.objects.all()
    return render(request, 'message_view.html', {'contacts': contacts})

def disease_view(request):
    # Get all registrations and their associated predictions
    registrations = Registration.objects.all()
    predictions = PredictionRequest.objects.all()

    # Create a dictionary to map user IDs to their predictions
    user_predictions = {}
    for prediction in predictions:
        user_id = prediction.user.id  # Assuming you have a foreign key to Registration in PredictionRequest
        if user_id not in user_predictions:
            user_predictions[user_id] = []
        user_predictions[user_id].append(prediction)

    # Create a list of user details with their predictions
    user_details = []
    for registration in registrations:
        user_prediction_list = user_predictions.get(registration.id, [])
        user_details.append({
            'profile': registration,
            'predictions': user_prediction_list
        })

    context = {
        'user_details': user_details
    }
    return render(request, 'disease_view.html', context)

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = HttpResponse(content_type='application/pdf')
    pisa_status = pisa.CreatePDF(html, dest=result)
    if pisa_status.err:
        return HttpResponse('We had some errors with code %s' % pisa_status.err)
    return result

def download_pdf_view(request):
    # Retrieve prediction and remedies from session
    predicted_disease = request.session.get('predicted_disease', 'Unknown Disease')
    remedies_and_medicines = request.session.get('remedies_and_medicines', default_message)

    # Prepare the context for the PDF
    context = {
        'prediction': predicted_disease,  # Disease predicted
        'medicine': remedies_and_medicines.split('Remedies:')[0].strip(),  # Medicines part
        'remedies': remedies_and_medicines.split('Remedies:')[1].strip() if 'Remedies:' in remedies_and_medicines else 'No remedies available.'  # Remedies part
    }

    # Render the PDF
    return render_to_pdf('pdf_template.html', context)
