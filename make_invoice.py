import argparse
import os
import yaml
import companyspecific

BASEPATH = companyspecific.BASEPATH
TEMPLATEPATH = companyspecific.TEMPLATEPATH

parser = argparse.ArgumentParser(description='Invoice generation script')
parser.add_argument('--month', '-m', action="store", type=str,
                   help='month of the invoices to be generated, eg:  201910')

args = parser.parse_args()
year = args.month[0:4]
month = args.month[4:]

## Generate yml files
# check the latest invoice counter
# first check in the current folder for existing yml files
latest = 0
checking_month = int(month)
while (latest == 0):
    path = BASEPATH + year + '/' + str(checking_month) + "/outgoing/"
    for root, dirs, files in os.walk(path):
        for file in files:
            if ".yml" in file:
                if (file[:10].isdigit()):
                    if int(file[:10])>latest:
                        latest=int(file[:10])
    checking_month = checking_month - 1
    #Exception for start of new year
    if checking_month == 0:
        break
print "Last used invoice number: " + str(latest)
if latest == 0:
    next = int(year)*1000000
else:
    next = latest + 1

# find all active customers
customerlist = companyspecific.customerlist
exceptionlist = companyspecific.exceptionlist

#for customer in customerlist:
    # find billing information for the customer
    # get the invoice data
    # write the yml file


#TODO '---' at the end needs to be removed for python but added for pandoc
# increment the invoice counter and append to the filename
for customer in customerlist:
    if customer in exceptionlist:
        continue
    path = BASEPATH + year + '/' + month + "/outgoing/" + customer + '/'
    for root, dirs, files in os.walk(path):
        for file in files:
            if ".yml" in file:
                with open(path+file) as f:
                     list_doc = yaml.load(f)
                #TODO doesn't seem to work
                list_doc["invoice-nr"] = str(next)
                print "added invoice-nr (" + str(next) + ") to: " + file
                with open(file, "w") as f:
                    yaml.dump(list_doc, f)
                os.system("mv " + path + file + " " + path + str(next) + '-' + file)
                next = next + 1

## Generate pdf timesheets to go with the invoices

## Generate pdf invoice based on yml files
for customer in customerlist:
    if customer in exceptionlist:
        continue
    path = BASEPATH + year + '/' + month + "/outgoing/" + customer + '/'
    file = makepdf(path)
    if not(file == ""):
        ## Compose the email
        composeEmail(file)

def makepdf(path):
    os.system("cp " + path + "*.yml " + TEMPLATEPATH)
    os.system("make")
    for root, dirs, files in os.walk(path):
        for file in files:
            if ".yml" in file:
                #print file
                os.system("cp " + TEMPLATEPATH + "*.pdf " + path + file[:-3] + "pdf")
                #cleanup
                os.system("rm " + TEMPLATEPATH + "*.yml")
                os.system("rm " + TEMPLATEPATH + "*.pdf")
                break
        else:
            print "yml filename not found"
            return ""
    return file

def composeEmail(file):
    with open(file) as f:
         list_doc = yaml.load(f)
    email = {"from":companyspecific.fromemail,
        "to": list_doc["to-email"],
        "cc": list_doc["cc-email"],
        "bcc":companyspecific.bccemail,
        "subject": "Invoice " + list_doc["invoice-nr"]
        }
    #email["attachment"] = "" #TODO add attachments
    email["body"] = """Dear Customer,

        Please find your invoice attached to this e-mail.
        Further detail regarding the invoice items can be found in """
    if  (list_doc["timetracking"]=="True"):
        email["body"] = email["body"] + "your timetracking system."
    else:
        email["body"] = email["body"] + "the accompanying ZIP file."
    email["body"] = email["body"] + """

        The invoice is generated in PDF format and replaces the paper copy.

        Payment can be made to Voltza by bank transfer to the bank specified at the bottom of your invoice. Please include your invoice number as the transaction reference.

        For any questions concerning this invoice: contact us at invoices@voltza.be

        Yours sincerely,

        Koenraad Van den Eeckhout"""
    os.system("thunderbird -compose " + ",".join(['%s=%s' % (key, value) for (key, value) in email.items()]))
