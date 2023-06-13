import logging
from datetime import datetime

from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db import OperationalError, IntegrityError
from django.shortcuts import render, redirect
from django.utils.timezone import make_aware

from .models import *


def view_index(request):
    return render(request, 'index.html')


def view_registration(request):
    if request.method == "GET":
        return render(request, 'registration.html')

    if request.method == "POST":
        fn = request.POST.get('first_name')
        ln = request.POST.get('last_name')
        sc = request.POST.get('subcontractor_code')
        em = request.POST.get('mail')
        pwd = request.POST.get('password')

        if not sc:
            username = (fn.lower() + ln.lower()).replace(" ", "")  # Generate username without spaces
        else:
            username = sc

        try:
            user_model = get_user_model()
            user = user_model.objects.create_user(first_name=fn, last_name=ln, username=username, password=pwd,
                                                  email=em)
            EmployeeDetails.objects.create(user=user)
            error = "No"
            cause = ""

        except IntegrityError as ex:
            logging.error(ex)
            cause = ex.args[0].split('.')[1]
            error = "Yes"

        except OperationalError as ex:
            logging.error(ex)
            cause = ex.args[0]
            error = "Yes"

        except Exception as ex:
            logging.error(ex)
            cause = ex
            error = "Yes"

        context = {
            'error': error,
            'cause': cause,
        }

        return render(request, 'registration.html', context)


def view_login(request):
    if request.method == 'POST':
        mail = request.POST.get('mail')
        pwd = request.POST.get('password')

        user_model = get_user_model()
        user = user_model.objects.filter(email=mail).first()

        context = {}

        if user is None:
            context['error'] = "Yes"
        else:
            auth_user = authenticate(request, username=user.username, password=pwd)

            if auth_user is not None:
                login(request, auth_user)
                context['error'] = "No"
            else:
                context['error'] = "Yes"

        return render(request, 'emp_log.html', context)

    return render(request, 'emp_log.html')


def view_homepage(request):
    if not request.user.is_authenticated:
        return redirect('emp_login')
    return render(request, 'emp_home.html')


@login_required
def view_profile(request):
    error = ""
    user = request.user
    try:
        employee = EmployeeDetails.objects.get(user=user)
    except EmployeeDetails.DoesNotExist:
        employee = None

    if request.method == "POST":
        # Retrieve form data from POST request
        fn = request.POST.get('first_name', '')
        ln = request.POST.get('last_name', '')
        sc = request.POST.get('subcontractor_code', '')
        dep = request.POST.get('department', '')
        fct = request.POST.get('function', '')
        con = request.POST.get('contact', '')
        jd = request.POST.get('join_date', '')
        gd = request.POST.get('gender', None)

        # Update user and employee fields
        user.first_name = fn
        user.last_name = ln
        user.username = sc or (fn.lower() + ln.lower())  # Set username as sccode or combination of first and last name

        if employee:
            employee.department = dep
            employee.function = fct
            employee.contact = con
            employee.join_date = jd
            employee.gender = gd
        else:
            # Create new EmployeeDetails object if it doesn't exist for the user
            employee = EmployeeDetails(user=user, empdep=dep, function=fct, contact=con, join_date=jd, gender=gd)

        try:
            user.save()
            employee.save()
            # Handle successful save or update
        except Exception as ex:
            logging.error(ex)

        return redirect('profile')

    # Handle GET request
    employee.join_date = employee.join_date.strftime('%Y-%m-%d') if employee and employee.join_date else ''
    if not employee.user.username.isdigit():
        employee.user.username = ""

    context = {
        'employee': employee,
        'error': error,
    }

    return render(request, 'profile.html', context)


def view_experience(request):
    user = request.user

    if request.method == 'POST':
        company = request.POST.get('company', '')
        position = request.POST.get('position', '')
        start_date = request.POST.get('start_date', '')
        end_date = request.POST.get('end_date', '')
        description = request.POST.get('description', '')

        if start_date:  # Ensure start_date is not empty
            start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:  # Ensure end_date is not empty
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

        try:
            EmployeeExperience.objects.create(
                employee=user,
                company=company,
                position=position,
                start_date=start_date,
                end_date=end_date,
                description=description
            )
            # Handle successful insertion
        except IntegrityError as ex:
            logging.error(ex)  # Print integrity error to the console
            context = {
                'error': "Yes",
            }
            return render(request, 'experience.html', context)

    elif request.method == 'GET':
        # Retrieve all existing entries for the user
        experiences = EmployeeExperience.objects.filter(employee=user)

        # Serialize the experiences into a list of dictionaries
        serialized_experiences = []

        for experience in experiences:
            serialized_experiences.append({
                'id': experience.id,
                'company': experience.company,
                'position': experience.position,
                'start_date': experience.start_date,
                'end_date': experience.end_date,
                'description': experience.description,
            })

        context = {
            'experiences': serialized_experiences
        }

        return render(request, 'experience.html', context)


def view_education(request):
    user = request.user
    error = "No"

    if request.method == 'POST':
        institution = request.POST.get('institution', '')
        degree = request.POST.get('degree', '')
        start_date = request.POST.get('start_date', '')
        end_date = request.POST.get('end_date', '')
        description = request.POST.get('description', '')

        if start_date:  # Ensure start_date is not empty
            start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:  # Ensure end_date is not empty
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

        try:
            EmployeeEducation.objects.create(
                employee=user,
                institution=institution,
                degree=degree,
                start_date=start_date,
                end_date=end_date,
                description=description
            )
            # Handle successful insertion
        except IntegrityError as ex:
            logging.error(ex)  # Print integrity error to the console
            context = {
                'error': "Yes",
            }
            return render(request, 'education.html', context)

        return redirect('education')

    elif request.method == 'GET':
        # Retrieve all existing entries for the user
        educations = EmployeeEducation.objects.filter(employee=user)

        # Serialize the educations into a list of dictionaries
        serialized_educations = []

        for education in educations:
            serialized_educations.append({
                'id': education.id,
                'institution': education.institution,
                'degree': education.degree,
                'start_date': education.start_date,
                'end_date': education.end_date,
                'description': education.description,
            })

        context = {
            'educations': serialized_educations
        }

        return render(request, 'education.html', context)


def view_remove_experience(request):
    if request.method == 'POST':
        row_id = request.POST.get('row_id')

        try:
            experience = EmployeeExperience.objects.get(id=row_id)
            experience.delete()
        except EmployeeExperience.DoesNotExist:
            pass

    return redirect('experience')


def view_remove_education(request):
    if request.method == 'POST':
        row_id = request.POST.get('row_id')

        try:
            education = EmployeeEducation.objects.get(id=row_id)
            education.delete()
        except EmployeeEducation.DoesNotExist:
            pass

    return redirect('education')


@login_required
def view_password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Update the session with the new password hash
            return redirect('emp_home')  # Redirect to the home page or any other desired page
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'password_change.html', {'form': form})


def view_logout(request):
    logout(request)
    return redirect('index')


@login_required
def view_delete_account(request):
    if request.method == 'POST':
        # Delete the user account
        user = request.user
        user.delete()
        logout(request)
        return redirect('index')  # Replace 'home' with the appropriate URL name for your home page

    return render(request, 'delete_account.html')  # Create the delete_account.html template
