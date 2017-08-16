from django.shortcuts import render
from django.template.loader import render_to_string
from django.template import RequestContext
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from .helpers import valid_leave_application
from .forms import FacultyStaffLeave
from .models import Leave, ApplicationRequest
from user_profile.models import Designated, Designation
from django.contrib.auth.models import User
from django.db.models import Q

# Create your views here.

#To get all the application requests pending for the current user
@login_required(login_url='/accounts/login')
def get_applications(request):
    if request.user.application_request.all().count() != 0:
        applications = request.user.application_request.all()
        return render(request, 'leaveapplication/application_request.html', {'user': request.user, 'applications':applications})
    return HttpResponse('No Pending Requests')


@login_required(login_url='/accounts/login')
def approve_application(request, id):

    try:
        application = ApplicationRequest.objects.get(id=id)

    except:

        return HttpResponse('Application does not exist !')

    if application.recipient == request.user:

        print('okay 1')

        if application.leave.replacing_user == request.user:

            print('is replacing user')

            application.leave.application_status = 'processing'

            try:

                if application.user.details.user_type == 'staff':

                    des = Designation.objects.get(designation='Registrar', user_type='staff')
                    hod = Designated.objects.filter(designation=des)[0]
                    ApplicationRequest.objects.create(user=application.user, recipient=hod, leave=application.leave)
                    application.delete()

                    return HttpResponse('success')

                else:

                    des = Designation.objects.filter(designation='HOD', user_type='faculty')

                    hods = Designated.objects.filter(designation=des)
                    required_departement = application.user.details.department
                    hod = list(filter(lambda x: x.user.details.department == required_departement, hods))[0].user

                    ApplicationRequest.objects.create(user=application.user, recipient=hod, leave=application.leave)
                    application.delete()

                    return HttpResponse('success')

            except Exception as e:
                return HttpResponse(e)#'HOD does not exist in database !')

        else:
            designation = request.user.designation.designation.designation
            # if request.user in Designated.objects.filter(user=request.user, designation=Designation.objects.get(designation='Director', user_type='faculty'))[0].user:
            condition = request.user.details.department == application.user.details.department
            if designation == 'HOD' and condition:
                application.leave.application_status = 'accepted'
                # ApplicationRequest.objects.create(user=application.user, recipient=hod, leave=application.leave)
                application.delete()

                return HttpResponse('success')

            else:

                try:

                    if application.user.details.user_type == 'staff':
                        des = Designation.objects.get(designation='Registrar', user_type='staff')

                    else:
                        des = Designation.objects.get(designation='HOD', user_type='faculty')

                except:
                    return HttpResponse('HOD does not exist in database !')

                if Designated.objects.filter(user=application.recipient, designation=des):

                    hods = Designated.objects.filter(user=application.recipient, designation=des).values('user')

                    if request.user in hods:
                        application.leave.application_status = 'accepted'
                        ApplicationRequest.objects.create(user=application.user, recipient=hod, leave=application.leave)
                        application.delete()

                        return HttpResponse('success')

                    else:
                        return HttpResponse('Unauthorised 1')
                else:
                    return HttpResponse('Unauthorised 2')
    else:
        return HttpResponse('Unauthorised 3')



@login_required(login_url='/accounts/login')
def main_interface(request):

    if request.method == 'POST':

        form = FacultyStaffLeave(request.POST, user=request.user)

        if form.is_valid():
            replacing_user = User.objects.get(username=form.cleaned_data['replacing_user'])
            leave = Leave.objects.create(
                applicant = request.user,
                replacing_user = replacing_user,
                type_of_leave = form.cleaned_data['type_of_leave'],
                start_date = form.cleaned_data['start_date'],
                end_date = form.cleaned_data['end_date'],
                purpose = form.cleaned_data['purpose'],
                leave_address = form.cleaned_data['leave_address'],
            )

            ApplicationRequest.objects.create(
                user = request.user,
                recipient = replacing_user,
                leave = leave,
            )
            return render(request, 'leaveapplication/apply.html')
        return render(request, 'leaveapplication/apply.html', {'form': form})

    form = FacultyStaffLeave(initial={})
    # response = render_to_string('leaveapplication/application_form.html', request=request, context={'form': form})
    # return JsonResponse({'data': response, 'other': 'otherdata'})
    return render(request, 'leaveapplication/application_form.html', {'form': form})
