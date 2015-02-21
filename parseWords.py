import mailbox
import csv
from parseDates import parseDate
import re
import string

def getcharsets(msg):
    charsets = set({})
    for c in msg.get_charsets():
        if c is not None:
            charsets.update([c])
    return charsets

def handleerror(errmsg, emailmsg,cs):
    print(errmsg)
    print("This error occurred while decoding with ",cs," charset.")
    print("These charsets were found in the one email.",getcharsets(emailmsg))
    print("This is the subject:",emailmsg['subject'])
    print("This is the sender:",emailmsg['From'])

def getbodyfromemail(msg):
    body = None
    #Walk through the parts of the email to find the text body.    
    if msg.is_multipart():    
        for part in msg.walk():

            # If part is multipart, walk through the subparts.            
            if part.is_multipart(): 

                for subpart in part.walk():
                    if subpart.get_content_type() == 'text/plain':
                        # Get the subpart payload (i.e the message body)
                        body = subpart.get_payload(decode=True) 
                        #charset = subpart.get_charset()

            # Part isn't multipart so get the email body
            elif part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True)
                #charset = part.get_charset()

    # If this isn't a multi-part message then get the payload (i.e the message body)
    elif msg.get_content_type() == 'text/plain':
        body = msg.get_payload(decode=True) 

   # No checking done to match the charset with the correct part. 
    for charset in getcharsets(msg):
        try:
            body = body.decode(charset)
        except LookupError:
            handleerror("LookupError: encountered.", msg,charset)
        except UnicodeEncodeError:
            handleerror("UnicodeEncodeError: encountered.",msg,charset)
        except UnicodeDecodeError:
            handleerror("UnicodeDecodeError: encountered.",msg,charset)
        except AttributeError:
             handleerror("AttributeError: encountered" ,msg,charset)
    return body    


''' ___MAIN___ '''

writer = csv.writer(open("wordFrequency.csv", "wb"))

words = dict()
dates = dict()
days = dict()

emailCount = 0

for message in mailbox.mbox('mail.mbox'):

    day, month, year, date = parseDate(message['date'])

    # body contains lowercase only, no numbers either
    body = getbodyfromemail(message)
    if body is None:
        body = "None"

    try:
        body = body.encode('ascii', 'ignore')
        body = body.lower()

        table = string.maketrans("","")
        body = body.translate(table, string.punctuation)
        
        # Split by any puncuiation, i.e. \r, \n, \t, ' '
        body = re.findall(r"[\w']+", body)


    except UnicodeEncodeError:
        print "UnicodeEncodeError!"
        body = "None"
    except UnicodeDecodeError:
        print "UnicodeDecodeError!"
        body = "None"
    except AttributeError:
        print "AttributeError!"
        body = "None"

    print 'count: ', emailCount
    emailCount += 1

    # Count for each word
    for word in body:
        if word is None or word.find('0x') is not -1:
            word = None
        if word is not None and word.find("http") is -1:
            if len(word) < 26 and len(word) > 2:
                word = re.sub(r'\d', '', word)
                if word not in words:
                    words[word] = 1
                else:
                    words[word] += 1

    # Count for each day
    if day not in days:
        days[day] = 1
    else:
        days[day] += 1

    # Count for each date
    if date not in dates:
        dates[date] = 1
    else:
        dates[date] += 1

writer.writerow("Word", "Count")
for word in words:
    print word, words[word]
    writer.writerow([word.encode('utf8'), words[word]])
