from django.shortcuts import render
import requests
from django.conf import settings as config
import json
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View
import base64
import io as BytesIO
from django.http import HttpResponse

# Create your views here.
class UserObjectMixin(object):
    model =None
    session = requests.Session()
    session.auth = config.AUTHS
    def get_object(self,endpoint):
        response = self.session.get(endpoint, timeout=10).json()
        return response

class registrationRetention(UserObjectMixin,View):
    def get(self,request):
        try:
            userId=request.session['UserID']
            LTR_Name = request.session['LTR_Name']
            LTR_Email = request.session['LTR_Email']
            Retention= config.O_DATA.format(f"/QYRetension?$filter=User_code%20eq%20%27{userId}%27")
            response = self.get_object(Retention)
            OpenProducts = [x for x in response['value'] if x['Status'] == 'Open']
            Pending = [x for x in response['value'] if x['Status'] == 'Processing']
            Approved = [x for x in response['value'] if x['Status'] == 'Approved']
            Rejected = [x for x in response['value'] if x['Status'] == 'Rejected']

            Access_Point= config.O_DATA.format(f"/QYRegistration?$filter=User_code%20eq%20%27{userId}%27")
            RetResponse = self.get_object(Access_Point)
            ApprovedProd = [x for x in RetResponse['value'] if x['Status'] == 'Approved']
            
            VertinaryClass = config.O_DATA.format(f"/QYVertinaryclasses")
            VertResponse = self.get_object(VertinaryClass)
            VertinaryClasses = [x for x in VertResponse['value']]

            variation= config.O_DATA.format(f"/QYVariation?$filter=User_code%20eq%20%27{userId}%27")
            VariationResponse = self.get_object(variation)

            ApprovedVariation = [x for x in VariationResponse['value'] if x['Status'] == 'Approved']

        except requests.exceptions.RequestException as e:
            messages.error(request,e)
            print(e)
            return redirect('retention')
        except KeyError as e:
            messages.info(request,"Session Expired, Login Again")
            print(e)
            return redirect('login')
        openCount = len(OpenProducts)
        pendCount = len(Pending)
        appCount = len(Approved)
        rejectedCount = len(Rejected)
        print(pendCount)
        ctx = {"openCount":openCount,"open":OpenProducts,"ApprovedVariation":ApprovedVariation,
        "pendCount":pendCount,"pending":Pending,"appCount":appCount,"approved":Approved,
        "rejectedCount":rejectedCount,"rejected":Rejected,"product":ApprovedProd,"LTR_Name":LTR_Name,"LTR_Email":LTR_Email, 
        "VertinaryClasses": VertinaryClasses}
        return render(request,"retention.html",ctx)
    def post(self,request):
        if request.method == 'POST':
            try:
                retNo = request.POST.get('retNo')
                myAction = request.POST.get('myAction')
                prodNo = request.POST.get('prodNo')
                changesToTheProduct = eval(request.POST.get('changesToTheProduct'))
                variations = request.POST.get('variation')
                iAgree = eval(request.POST.get('iAgree'))
                VariationNumber = request.POST.get('VariationNumber')
                signatoryName = request.POST.get('signatoryName')
                signatoryPosition = request.POST.get('signatoryPosition')

                if not iAgree:
                    iAgree = False
                if not variations:
                    variations = 'False'
                if not VariationNumber:
                    VariationNumber = ''
                
                variation = eval(variations)

                response = config.CLIENT.service.Retension(retNo,myAction,request.session['UserID'],prodNo,
                VariationNumber,changesToTheProduct,variation,iAgree,signatoryName,signatoryPosition)
                print(response)
                if response == True:
                    messages.success(request,"Request Successful")
                    return redirect('retention')
            except KeyError as e:
                messages.info(request,"Session Expired, Login Again")
                print(e)
                return redirect('login') 
            except Exception as e:
                print(e)
                messages.error(request,e)
                return redirect('retention')
        return redirect('retention')
    

class retentionDetails(UserObjectMixin,View):
    def get(self,request,pk):
        try:
            userID =request.session['UserID']
            LTR_Name = request.session['LTR_Name']
            LTR_Email = request.session['LTR_Email']
            Access_Point = config.O_DATA.format(f"/QYRetension?$filter=User_code%20eq%20%27{userID}%27%20and%20Retension_No_%20eq%20%27{pk}%27")
            response = self.get_object(Access_Point)

            for res in response['value']:
                responses = res
                Status = res['Status']
                prod = res['ProductNo']
                
            vet_class = '' 
            Product = config.O_DATA.format(f"/QYRegistration?$filter=ProductNo%20eq%20%27{prod}%27")
            prod_details = self.get_object(Product)
            for prod_No in prod_details['value']:
                prod_res = prod_No
                vet_class = prod_res['Veterinary_Classes']
                print(vet_class)
                
                
            VertinaryClass = config.O_DATA.format(f"/QYVertinaryclasses?$filter=Class%20eq%20%27{vet_class}%27")
            VertResponse = self.get_object(VertinaryClass)
            for vertinary_class in VertResponse['value']:
                VertinaryClasses = vertinary_class
                print(VertinaryClasses)
            
        except requests.exceptions.RequestException as e:
            messages.error(request,e)
            print(e)
            return redirect('retention')
        except KeyError as e:
            messages.info(request,"Session Expired, Login Again")
            print(e)
            return redirect('login')
        
        ctx = {"res":responses,"status":Status,"LTR_Name":LTR_Name,"LTR_Email":LTR_Email, 
               "VertinaryClasses":VertinaryClasses,}
        return render(request,'RetentionDetails.html',ctx)

class retentionGateway(UserObjectMixin,View):
    def get(self,request,pk):
        try:
            userID = request.session['UserID']
            LTR_Name = request.session['LTR_Name']
            LTR_Email = request.session['LTR_Email']
            Access_Point = config.O_DATA.format(f"/QYRetension?$filter=User_code%20eq%20%27{userID}%27%20and%20Retension_No_%20eq%20%27{pk}%27")
            response = self.get_object(Access_Point)
            for res in response['value']:
                responses = res
                Status = res['Status']                
        except requests.exceptions.RequestException as e:
            messages.error(request,e)
            print(e)
            return redirect('retention')
        except KeyError as e:
            messages.info(request,"Session Expired, Login Again")
            print(e)
            return redirect('login')
        ctx = {"res":responses,"status":Status,"LTR_Name":LTR_Name,"LTR_Email":LTR_Email}
        return render(request,'retentionGateway.html',ctx)
    def post(self,request,pk):
        if request.method == 'POST':
            try:
                transactionCode = request.POST.get('transactionCode')
                currency = request.POST.get('currency')

                if not transactionCode:
                    messages.error(request, "Transaction Code can't be empty.")
                    return redirect('retentionGateway', pk=pk)
                if not currency:
                    messages.error(request, "Currency code missing please contact the system admin")
                    return redirect('retentionGateway', pk=pk)
                response = config.CLIENT.service.FnConfirmPayment(transactionCode,currency,pk,request.session['UserID'])
                print(response)
                if response == True:
                    messages.success(request,"Payment was successful. You can now submit your application.")
                    return redirect('retentionDetails', pk=pk)
                else:
                    messages.error(request, "Payment Not sent. Try Again.")
                    return redirect('retentionGateway', pk=pk)
            except requests.exceptions.RequestException as e:
                messages.error(request,e)
                print(e)
                return redirect('retentionGateway', pk=pk)
            except KeyError as e:
                messages.info(request,"Session Expired, Login Again")
                print(e)
                return redirect('login')
            except Exception as e:
                messages.error(request,e)
                return redirect('retentionGateway', pk=pk)
        return redirect('retentionGateway', pk=pk)

def SubmitRetention(request,pk):
    if request.method == 'POST':
        try:
            response = config.CLIENT.service.SubmitRetention(pk,request.session['UserID'])
            print(response)
            if response == True:
                messages.success(request,"Document submitted successfully.")
                return redirect('retentionDetails', pk=pk)
            else:
                print("Not sent")
                return redirect ('retentionDetails',pk=pk)
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
            return redirect ('retentionDetails',pk=pk)
    return redirect('retentionDetails', pk=pk)

class makeRetentionPayment(UserObjectMixin,View):
    def post(self, request,pk):
        if request.method == 'POST':
            try:
                retNo = pk
                userCode = request.session['UserID']
                print(retNo)

                response = config.CLIENT.service.FnRetetionPayment(retNo,userCode)
                print(response)
                if response == False:
                    messages.success(request,"Please Make Your payment and click confirm payment.")
                    return redirect('retentionGateway', pk=pk)
                if response == True:
                    messages.error(request,"False")
                    return redirect('retentionDetails', pk=pk)
            except KeyError as e:
                messages.info(request,"Session Expired, Login Again")
                print(e)
                return redirect('login')
            except Exception as e:
                print(e)
                messages.info(request,e)
                return redirect ('retentionDetails',pk=pk)
        return redirect('retentionDetails', pk=pk)

def FNGenerateRetentionInvoice(request, pk):
    if request.method == 'POST':
        try:
            response = config.CLIENT.service.FNGenerateRetentionInvoice(pk)
            buffer = BytesIO.BytesIO()
            content = base64.b64decode(response)
            buffer.write(content)
            responses = HttpResponse(
                buffer.getvalue(),
                content_type="application/pdf",
            )
            responses['Content-Disposition'] = f'inline;filename={pk}'
            return responses
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('retentionGateway', pk=pk)

def PrintRentetionCertificate(request, pk):
    if request.method == 'POST':
        try:
            response = config.CLIENT.service.PrintRentetionCertificate(pk)
            buffer = BytesIO.BytesIO()
            content = base64.b64decode(response)
            buffer.write(content)
            responses = HttpResponse(
                buffer.getvalue(),
                content_type="application/pdf",
            )
            responses['Content-Disposition'] = f'inline;filename={pk}'
            return responses
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('retentionDetails', pk=pk)


