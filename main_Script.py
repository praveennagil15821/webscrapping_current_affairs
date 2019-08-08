import urllib.request,urllib.parse,urllib.error
import requests
from bs4 import BeautifulSoup
from datetime import date
import calendar
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders
import os,re
from fpdf import FPDF
import subprocess


d=date.today()

mob_numbers='Mobile numbers you want to send sms to'
subscribed_mail=['List of reciever mail address']
url='https://www.gktoday.in'
way_url='https://www.way2sms.com/api/v1/sendCampaign'

def txt2pdf():
	pwd=os.getcwd()
	filename=f"{d.strftime('%b')},{str(d.year)}.txt"
	# python3_command = f'{pwd}/pytxt2pdf.py filename' # launch your python2 script using bash
	# #python3_command = f"pytxt2pdf.py "{d.strftime('%b')}, {str(d.year)}.txt"
	# process = subprocess.Popen(python3_command.split(), stdout=subprocess.PIPE)
	# output, error = process.communicate()  # receive output from the python2 script
	script = ["python", "pytxt2pdf.py", filename]    
	#process = subprocess.Popen(" ".join(script),shell=True,env={"PYTHONPATH": "."})
	process = subprocess.Popen(" ".join(script), shell=True,stdout=subprocess.PIPE)
	output, error = process.communicate()
	print(output,error)

def email():
	fromaddr = "Your Email Id"
	toaddr = subscribed_mail
	
	for send_to in toaddr:		   
		# instance of MIMEMultipart 
		msg = MIMEMultipart() 
		  
		# storing the senders email address   
		msg['From'] = fromaddr 
		  
		# storing the receivers email address  
		msg['To'] = send_to
		  
		# storing the subject  
		msg['Subject'] = f"Current Affairs of the Month {d.strftime('%b')} {d.year}"
		  
		# string to store the body of the mail 
		body = f"Current Affairs of the Month {d.strftime('%b')} {d.year} are in the attached file. Regards The-One."
		  
		# attach the body with the msg instance 
		msg.attach(MIMEText(body, 'plain')) 
		  
		# open the file to be sent  
		filename = f"{d.strftime('%b')},{d.year}.txt.pdf"
		attachment = open(f"{d.strftime('%b')},{d.year}.txt.pdf", "rb") 
		  
		# instance of MIMEBase and named as p 
		p = MIMEBase('application', 'octet-stream') 
		  
		# To change the payload into encoded form 
		p.set_payload((attachment).read()) 
		  
		# encode into base64 
		encoders.encode_base64(p) 
		   
		p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
		  
		# attach the instance 'p' to instance 'msg' 
		msg.attach(p) 
		  
		# creates SMTP session 
		s = smtplib.SMTP('smtp.gmail.com', 587) 
		  
		# start TLS for security 
		s.starttls() 
		  
		# Authentication 
		s.login(fromaddr, 'Email password') 
		  
		# Converts the Multipart msg into a string 
		text = msg.as_string() 
		  
		# sending the mail 
		s.sendmail(fromaddr, toaddr, text) 
		  
		# terminating the session 
		s.quit() 


def send_sms(data):
	
	data=data.encode('utf-8')
	
	url = "https://www.fast2sms.com/dev/bulk"
	payload = f"sender_id=FSTSMS&message={data}&language=english&route=p&numbers={mob_numbers}"
	headers = {
	'authorization': "Api key",
	'Content-Type': "application/x-www-form-urlencoded",
	'Cache-Control': "no-cache",
	}
	response = requests.request("POST", url, data=payload, headers=headers)
	print(response.text)

def sendPostRequest(reqUrl, apiKey, secretKey, useType, phoneNo, senderId, textMessage):
	req_params = {
	'apikey':apiKey,
	'secret':secretKey,
	'usetype':useType,
	'phone': phoneNo,
	'message':textMessage,
	'senderid':senderId
	}
	return requests.post(reqUrl, req_params)

	#------------------------------------------------------------------------------------


def filter_detail(url):
	html = urllib.request.urlopen(url).read()
	soup=BeautifulSoup(html,'html.parser')
	text=str()
	
	for element in soup.findAll('div', attrs={'class':'inside_post column content_width'}):
		heading=element.find('h1')		
		#print(heading.text)
		detail=element.findAll('p')
		remove=element.findAll('p',attrs={'class':'small-font'})
		other=element.findAll('li')
		final=[i for i in detail if i not in remove]
		final.extend(other)
	
	for i in final:text=text+(i.text)+'\n '	
	return text

def msg_filter(msg):
	msg=str(msg)
	msg=re.sub("[^a-zA-Z\d' ]+", ' ', msg)
	return msg



def start(url):
	msg_dict={}
	html = urllib.request.urlopen(url).read()
	soup=BeautifulSoup(html,'html.parser')
	overview=str()
	for element in soup.findAll('div', attrs={'class':'inside_post column content_width'}):	
		a=element.findAll('a',href=lambda href:href and "currentaffairs.gktoday.in" in href)
	
	#opening data storage files
	

	file = open(f"{d.strftime('%b')},{d.year}.txt","a")

	t = open(f"{d.strftime('%b')},{d.year}.txt","r")
	temp=t.read()
	t.close()

	check_list=open(f"{d.strftime('%b')},{d.year} links list.txt","a")
	c=open(f"{d.strftime('%b')},{d.year} links list.txt","r")
	confirm_list=c.read()
	confirm_list=confirm_list.split('~')
	c.close()
	new_day="-----------------------"+str(d.day)+" "+str(d.strftime('%b'))+" "+str(d.year)+"------------------------------"+'\n'

	# generate the new links data
	msg=str()
	for i in a:
		if i['href']!="http://currentaffairs.gktoday.in/" and i['href'] not in confirm_list:
			msg=msg+msg_filter(i.text)+' link : '+(i['href'])
			if new_day not in temp:
				file.write(new_day)
			link=i['href']+str('~')
			check_list.write(link)
			data=str((i.text)+'\n \n')		
			detail=filter_detail(i['href'])
			new_line="vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv"+'\n'
			overview=overview+'\n\n'+str(i.text)+'\n'+str(i['href'])
			data=data+detail
			file.write(data)
			file.write(new_line)
	
	msg_dict['msg']=str(msg)
	
	file.close()
	check_list.close()

	#email the monthly data
	if d.day==calendar.monthrange(d.year, d.month)[1]:
	#if d.day==8:
		txt2pdf()
		email()
		way2_credentials=['api id', 'key',]
		numbers=mob_numbers.split(',')
		for num in numbers:
			print('Sending monthly sms to ',num)
			response = sendPostRequest(way_url, way2_credentials[0],way2_credentials[1],'stage', num, 'sender id ', 'Monthly Current affairs are available on your mail. Regards The-One' )
				
			print('monthly sms sent',response)

		
		# if os.path.exists(f"{d.strftime('%b')}, {d.year} links list.txt"):
		#   os.remove(f"{d.strftime('%b')}, {d.year} links list.txt")

		# if os.path.exists(f"{d.strftime('%b')}, {d.year}.txt"):
		#   os.remove(f"{d.strftime('%b')}, {d.year}.txt")
		# if os.path.exists(f"{d.strftime('%b')}, {d.year}.txt.pdf"):
		#   os.remove(f"{d.strftime('%b')}, {d.year}.txt.pdf")
	#print(msg_dict['msg'])
	return msg_dict['msg']
		
		  
#main calling 


msg=start(url)
if msg:
	print(True)
	send_sms(msg)

