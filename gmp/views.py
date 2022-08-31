import base64
from django.shortcuts import render, redirect
import requests
import json
from django.conf import settings as config
from django.contrib import messages
from django.views import View

# Create your views here.
class UserObjectMixin(object):
    model =None
    session = requests.Session()
    session.auth = config.AUTHS
    def get_object(self,endpoint):
        response = self.session.get(endpoint, timeout=10).json()
        return response

class GMPApplication(UserObjectMixin,View):
    def get(self,request):
        try:
            userID = request.session['UserID']
            Retention= config.O_DATA.format(f"/QYGMP?$filter=User_code%20eq%20%27{userID}%27")
            response = self.get_object(Retention)
            OpenProducts = [x for x in response['value'] if x['Status'] == 'Open']
            Pending = [x for x in response['value'] if x['Status'] == 'Processing']
            Approved = [x for x in response['value'] if x['Status'] == 'Approved']
            Rejected = [x for x in response['value'] if x['Status'] == 'Rejected']

            CountriesRegistered = config.O_DATA.format("/QYCountries")
            CountryResponse = self.get_object(CountriesRegistered)
            resCountry = CountryResponse['value']

        except requests.exceptions.RequestException as e:
            messages.error(request,e)
            print(e)
            return redirect('gmp')
        except KeyError as e:
            messages.info(request,"Session Expired, Login Again")
            print(e)
            return redirect('login')
        openCount = len(OpenProducts)
        pendCount = len(Pending)
        appCount = len(Approved)
        rejectedCount = len(Rejected)
        ctx = {"openCount":openCount,"open":OpenProducts,
        "pendCount":pendCount,"pending":Pending,"appCount":appCount,"approved":Approved,
        "rejectedCount":rejectedCount,"rejected":Rejected,
        "country":resCountry}
        return render(request,'gmp.html',ctx)
    def post(self, request):
        if request.method == "POST":
            try:
                gmpNo = request.POST.get('gmpNo')
                myAction= request.POST.get('myAction')
                SitePhysicalAddress = request.POST.get('SitePhysicalAddress')
                SiteCountry = request.POST.get('SiteCountry')
                SiteTelephone = request.POST.get('SiteTelephone')
                SiteMobile = request.POST.get('SiteMobile')
                SiteEmail = request.POST.get('SiteEmail')
                isContact = request.POST.get('isContact')
                ContactName =request.POST.get('ContactName')
                ContactTel = request.POST.get('ContactTel')
                ContactEmail = request.POST.get('ContactEmail')
                VeterinaryMedicines = int(request.POST.get('VeterinaryMedicines'))
                TypeOfInspection = int(request.POST.get('TypeOfInspection'))
                stateOther = request.POST.get('StateOther')
                iAgree = eval(request.POST.get('iAgree'))

                if not iAgree:
                    iAgree = False
                if not ContactName:
                    ContactName = ''

                if not ContactTel:
                    ContactTel = ''

                if not ContactEmail:
                    ContactEmail = ''

                if not stateOther:
                    stateOther = ''

                response = config.CLIENT.service.GMP(gmpNo,myAction,request.session['UserID'],SitePhysicalAddress,
                SiteCountry,SiteTelephone,SiteMobile,SiteEmail,isContact,ContactName,ContactTel,ContactEmail,
                VeterinaryMedicines,TypeOfInspection,stateOther,iAgree
                )
                print(response)
                if response == True:
                    messages.success(request,"Saved Successfully")
                    return redirect('gmp')

            except requests.exceptions.RequestException as e:
                print(e)
                return redirect('gmp')
            except KeyError as e:
                messages.info(request,"Session Expired, Login Again")
                print(e)
                return redirect('login')
        return redirect('gmp')


class GMPDetails(UserObjectMixin,View):
    def get(self,request,pk):
        try:
            userID =request.session['UserID']
            Access_Point = config.O_DATA.format(f"/QYGMP?$filter=User_code%20eq%20%27{userID}%27%20and%20GMP_No_%20eq%20%27{pk}%27")
            response = self.get_object(Access_Point)
            for res in response['value']:
                responses = res
                Status = res['Status']

            Lines = config.O_DATA.format(f"/QYLinestobeInspected?$filter=No%20eq%20%27{pk}%27%20and%20User_code%20eq%20%27{userID}%27")
            linesResponse = self.get_object(Lines)
            Line = [x for x in linesResponse['value']]

            ManufacturesParticulars = config.O_DATA.format(f"/QYGmpManufactureDetails?$filter=AuxiliaryIndex2%20eq%20%27{pk}%27")
            ManufacturerResponse = self.get_object(ManufacturesParticulars)
            Manufacturer = [x for x in ManufacturerResponse['value']]

            Countries = config.O_DATA.format("/QYCountries")
            CountryResponse = self.get_object(Countries)
            resCountry = CountryResponse['value']

            Attachments = config.O_DATA.format("/QYGMPRequiredDocuments")
            AttachResponse = self.get_object(Attachments)
            attach = AttachResponse['value']

            AllAttachments = config.O_DATA.format(f"/QYGMPAttachments?$filter=No_%20eq%20%27{pk}%27%20and%20Table_ID%20eq%2050004")
            AllAttachResponse = self.get_object(AllAttachments)
            Files = [x for x in AllAttachResponse['value']]

        except requests.exceptions.RequestException as e:
            messages.error(request,e)
            print(e)
            return redirect('GMPDetails', pk=pk)
        except KeyError as e:
            messages.info(request,"Session Expired, Login Again")
            print(e)
            return redirect('login')
        
        ctx = {"res":responses,"status":Status,"line":Line,"manufacturer":Manufacturer,
        "country":resCountry,"files": Files,"attach":attach}
        return render(request,"gmpDetails.html",ctx)

def linesToInspect(request,pk):
    if request.method == "POST":
        try:
            myAction= 'insert'
            DosageForm = int(request.POST.get('DosageForm'))
            otherDosage = request.POST.get('otherDosage')
            Activity = int(request.POST.get('Activity'))

            if not otherDosage:
                otherDosage = ''
            try:
                response = config.CLIENT.service.LinesInspected(pk,myAction,request.session['UserID'],DosageForm,
                otherDosage,Activity)
                print(response)
                if response == True:
                    messages.success(request,"Saved Successfully")
                    return redirect('GMPDetails',pk=pk)
            except Exception as e:
                print(e)
                messages.error(request,e)
                return redirect('GMPDetails',pk=pk)
        except KeyError as e:
            messages.info(request,"Session Expired, Login Again")
            print(e)
            return redirect('login')
    return redirect('GMPDetails',pk=pk)

class GMPGateway(UserObjectMixin,View):
    def get(self,request,pk):
        try:
            userID = request.session['UserID']
            Access_Point = config.O_DATA.format(f"/QYGMP?$filter=User_code%20eq%20%27{userID}%27%20and%20GMP_No_%20eq%20%27{pk}%27")
            response = self.get_object(Access_Point)
            for res in response['value']:
                responses = res
                Status = res['Status']                
        except requests.exceptions.RequestException as e:
            messages.error(request,e)
            print(e)
            return redirect('gmp')
        except KeyError as e:
            messages.info(request,"Session Expired, Login Again")
            print(e)
            return redirect('login')
        ctx = {"res":responses,"status":Status}
        return render(request,'GMPGateway.html',ctx)
    def post(self,request,pk):
        if request.method == 'POST':
            try:
                transactionCode = request.POST.get('transactionCode')
                currency = request.POST.get('currency')

                if not transactionCode:
                    messages.error(request, "Transaction Code can't be empty.")
                    return redirect('GMPGateway', pk=pk)
                if not currency:
                    messages.error(request, "Currency code missing please contact the system admin")
                    return redirect('GMPGateway', pk=pk)
                response = config.CLIENT.service.FnConfirmPayment(transactionCode,currency,pk,request.session['UserID'])
                print(response)
                if response == True:
                    messages.success(request,"Payment was successful. You can now submit your application.")
                    return redirect('GMPDetails', pk=pk)
                else:
                    messages.error("Payment Not sent. Try Again.")
                    return redirect('GMPGateway', pk=pk)
            except requests.exceptions.RequestException as e:
                messages.error(request,e)
                print(e)
                return redirect('GMPGateway', pk=pk)
            except KeyError as e:
                messages.info(request,"Session Expired, Login Again")
                print(e)
                return redirect('login')
            except Exception as e:
                messages.error(request,e)
                return redirect('GMPGateway', pk=pk)
        return redirect('GMPGateway', pk=pk)


def SubmitGMP(request,pk):
    if request.method == 'POST':
        try:
            response = config.CLIENT.service.SubmitGMP(pk,request.session['UserID'])
            print(response)
            if response == True:
                messages.success(request,"Document submitted successfully.")
                return redirect('GMPDetails', pk=pk)
            else:
                print("Not sent")
                return redirect ('GMPDetails',pk=pk)
        except requests.exceptions.RequestException as e:
            messages.error(request,e)
            print(e)
            return redirect('Registration')
        except KeyError as e:
            messages.info(request,"Session Expired, Login Again")
            print(e)
            return redirect('login')
        except Exception as e:
            messages.error(request,e)
            return redirect ('GMPDetails',pk=pk)
    return redirect('GMPDetails', pk=pk)

def GMPManufactures(request,pk):
    if request.method == 'POST':
        try:
            prodNo = pk
            myAction = "insert"
            userId = request.session['UserID']
            manufacturerName = request.POST.get('manufacturerName')
            ManufacturerEmail= request.POST.get('ManufacturerEmail')
            postalAddress = request.POST.get('postalAddress')
            plantAddress = request.POST.get('plantAddress')
            ManufacturerTelephone = request.POST.get('ManufacturerTelephone')
            country = request.POST.get('country')
            activity = int(request.POST.get('activity'))
            TypeOfManufacturer = int(request.POST.get('TypeOfManufacturer'))
            manufacturerOther = request.POST.get('manufacturerOther')
            if not manufacturerOther:
                manufacturerOther = ''
            try:
                response = config.CLIENT.service.GMPManufactureDetails(prodNo,myAction,userId,
                manufacturerName,ManufacturerEmail,postalAddress,plantAddress,ManufacturerTelephone,
                country,activity,TypeOfManufacturer)
                print(response)
                if response == True:
                    messages.success(request,"Saved Successfully. Click Add New to create more  records")
                    return redirect('GMPDetails',pk=pk)
                else:
                    print("Not sent")
                    return redirect ('GMPDetails',pk=pk)
            except requests.exceptions.RequestException as e:
                print(e)
                return redirect('GMPDetails', pk=pk)
        except KeyError as e:
            messages.info(request,"Session Expired, Login Again")
            print(e)
            return redirect('login')
    return redirect('GMPDetails',pk=pk)

def GMPAttachement(request, pk):
    if request.method == "POST":
        try:
            attach = request.FILES.get('attachment')
            filename = request.FILES['attachment'].name
            name = request.POST.get('name')
            tableID = 50004
            attachment = base64.b64encode(attach.read())

            try:
                response = config.CLIENT.service.GMPAttachement(
                    pk, filename, attachment, tableID,name)
                print(response)
                if response == True:
                    messages.success(request, "Upload Successful")
                    return redirect('GMPDetails',pk=pk)
                else:
                    messages.error(request, "Failed, Try Again")
                    return redirect('GMPDetails',pk=pk)
            except Exception as e:
                messages.error(request, e)
                print(e)
                return redirect('GMPDetails',pk=pk)
        except Exception as e:
            print(e)
    return redirect('GMPDetails',pk=pk)

    # To check against the user code to see whether there are products registered