import argparse
import os
import yaml
import companyspecific
import datetime

BASEPATH = companyspecific.BASEPATH
TEMPLATEPATH = companyspecific.TEMPLATEPATH

def findnextinvoicenr(year, month):
    # check the latest invoice counter
    # first check in the current folder for existing yml files
    latest = 0
    while (latest == 0):
        path = BASEPATH + str(year) + '/' + '{0:02d}'.format(month) + "/outgoing/"
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if ".yml" in file:
                        #print file
                        if (file[:10].isdigit()):
                            if int(file[:10])>latest:
                                latest=int(file[:10])
        else:
            print "Path not found: " + path
        month = month - 1
        #Exception for start of new year
        if month == 0:
            break
    print "Last used invoice number: " + str(latest)
    if latest == 0:
        next = year*1000000
    else:
        next = latest + 1
    return next

def updateinvoicenr(file, invoicenr):
    with open(file) as f:
         list_doc = yaml.load(f)
    #TODO doesn't seem to work
    list_doc["invoice-nr"] = str(invoicenr)
    print "added invoice-nr (" + str(invoicenr) + ") to: " + file
    with open(file, "w") as f:
        f.write("---\n")
        yaml.dump(list_doc, f)
        f.write("...")
    filename = file.split('/')[-1]
    path = file[:-len(filename)]
    if len(filename.split('-'))>1 and filename.split('-')[0].isdigit():
        file = path + str(invoicenr) + '-' + filename.split('-')[1]
    else:
        file = path + str(invoicenr) + '-' + filename
    os.system("mv " + path + filename + " " + file)
    return file

def makeinvoice(file):
    now = datetime.datetime.now()
    next = findnextinvoicenr(now.year, now.month)
    file = updateinvoicenr(file, next)
    makepdf(file)
    composeEmail(file)

def makepdf(file):
    #TODO: fix bug when time is < 0.01 units
    os.system("cp " + file + " " + TEMPLATEPATH)
    os.system("make")
    #print file
    os.system("cp " + TEMPLATEPATH + "*.pdf " + file[:-3] + "pdf")
    #cleanup
    os.system("rm " + TEMPLATEPATH + "*.yml")
    os.system("rm " + TEMPLATEPATH + "*.pdf")

def composeEmail(file):
    with open(file) as f:
         list_doc = yaml.load(f)
    email = {"from":companyspecific.fromemail,
        "to": list_doc["to-email"],
        "bcc":companyspecific.bccemail,
        "subject": "Invoice " + str(list_doc["invoice-nr"])
        }
    if "cc-email" in list_doc.keys():
        email["cc"]= list_doc["cc-email"]
    email["attachment"] = file[:-3] + "pdf"
    #TODO more attachments
    if  (list_doc["timetracking"]==True):
        email["message"] = companyspecific.message_timetracking
    else:
        email["message"] = companyspecific.message_notimetracking
    os.system("thunderbird -compose \"" + ",".join(['%s=%s' % (key, value) for (key, value) in email.items()])+'\"')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Invoice generation script')
    parser.add_argument('--month', '-m', action="store", type=str,
                       help='month of the invoices to be generated, eg:  201910')
    parser.add_argument('--single', '-s', action="store", default="", type=str,
                       help='filename of single invoice to be generated, eg:  /home/user/test.yml')

    args = parser.parse_args()
    if not (args.single==""):
        makeinvoice(args.single)
    else:
        year = args.month[0:4]
        month = args.month[4:]

        ## Generate yml files
        # find all active customers
        customerlist = companyspecific.customerlist
        exceptionlist = companyspecific.exceptionlist

        #for customer in customerlist:
            # find billing information for the customer
            # get the invoice data
            # write the yml file

        # increment the invoice counter and append to the filename
        for customer in customerlist:
            if customer in exceptionlist:
                continue
            path = BASEPATH + year + '/' + month + "/outgoing/" + customer + '/'
            for root, dirs, files in os.walk(path):
                for file in files:
                    if ".yml" in file:
                        ## Generate pdf timesheets to go with the invoices
                        makeinvoice(path + file)
