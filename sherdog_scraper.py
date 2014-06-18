import urllib
import re
import csv
import sys
import time
import random

#run like:
# python yon_sherdog.py 1 100 fight_list.csv fight_metadata.csv

def build_method(fights_html):
    method_list = re.findall(r"(?<=<td>[A-Z])(.*?)(<br)", fights_html)
    num_fights = len(method_list)
    method = []
    for outcome in method_list:
        if outcome[0][0:3] == "O (":
            method.append("K" + outcome[0])
        if outcome[0][0:3] == "KO ":
            method.append("T" + outcome[0])
        if outcome[0][0:3] == "eci":
            method.append("D" + outcome[0])
        if outcome[0][0:3] == "raw":
            method.append("D" + outcome[0])
        if outcome[0][0:3] == "ubm":
            method.append("S" + outcome[0])
        if outcome[0][0:3] == "ech":
            method.append("T" + outcome[0])
        if outcome[0][0:3] == "Q (":
            method.append("D" + outcome[0])
    return method

def build_fighter_metadata(htmltext, fighter_num):
    bio_html = re.findall(r"(?<=vcard)((.|\n)*)(?=bio_graph\")", htmltext)[0][0]
    try:
        DOB = re.findall(r"(?<=itemprop=\"birthDate\">)(.*?)(?=<)", bio_html)[0]
    except:
        DOB = "NaN"
    try:
        nationality = re.findall(r"(?<=itemprop=\"nationality\">)(.*?)(?=<)", bio_html)[0]
    except:
        nationality = 'NaN'
    try:
        weight = re.findall(r"(?<=Weight<br />\n                                        <strong>)(.*?)(?=</strong>)", bio_html)[0]
    except:
        weight = "NaN"
    try:
        height = re.findall(r"(?<=Height<br />\n                                        <strong>)(.*?)(?=</strong>)", bio_html)[0]
    except:
        weight = "NaN"
    try:
        height = re.sub('["]', '', height)
    except:
        height = "Nan"
    meta = [fighter_num, DOB, height, weight, nationality]
    return meta

def build_fight_history(num):
    url = "http://www.sherdog.com/fighter/-%s" % num
    htmlfile = urllib.urlopen(url)
    htmltext = htmlfile.read(htmlfile)
    fighter_name_num = re.findall(r"(?<=content=\"http://www.sherdog.com/fighter/)(.*?)(?=\")", htmltext)[0]
    fighter_num = [int(s) for s in fighter_name_num.split('-') if s.isdigit()][0]
    fighter_name = " ".join(re.findall("[a-zA-Z]+", fighter_name_num))
    fights_html = re.findall(r"(?<=<h2>Fight History</h2>)((.|\n)*)(?=    </table>)", htmltext)
    fights_html = fights_html[0][0]
    result = re.findall(r"(?<=final_result )(.*?)(?=\")", fights_html)
    event = re.findall(r"(?<=/events/)(.*?)(?=\")", fights_html)
    date_ref= re.findall(r"(?<=sub_line\">)(.*?)(?=<)", fights_html)
    date = date_ref[::2]
    ref = date_ref[1::2]
    round = re.findall(r"(?<=<td>)(\d{1})(?=</td>)", fights_html)
    minutes = re.findall(r"(?<=<td>)(\d{1,2})(?=\:)", fights_html)
    seconds = re.findall(r"(?<=\:)(\d{2})(?=</td>)", fights_html)
    method = build_method(fights_html)
    opponent_name_num = re.findall(r"(?<=/fighter/)(.*?)(?=\")", fights_html)
    opponent_num = []
    opponent_name = []
    for opp in opponent_name_num:
        opponent_num.append([int(s) for s in opp.split('-') if s.isdigit()][0])
        opponent_name.append(" ".join(re.findall("[a-zA-Z]+", opp)))
    num_fights = len(method)
    fighter_name_extended = [fighter_name]*num_fights
    fighter_num_extended = [fighter_num]*num_fights
    fight_key = []
    for idx, opp_num in enumerate(opponent_num):
        if opp_num < fighter_num:
            fight_key.append(str(opp_num) + '-' + str(fighter_num) + '-' + date[idx])
        else:
            fight_key.append(str(fighter_num) + '-' + str(opp_num) + '-' + date[idx])
    fight_history = zip(fight_key, fighter_name_extended, fighter_num_extended, opponent_name, opponent_num, result, method, round, minutes, seconds, date, event, ref)
    meta = build_fighter_metadata(htmltext, fighter_num)
    return fight_history, meta

def build_database(list, output_database, output_metadata):
    with open(output_database, 'wb') as f:
        with open(output_metadata, 'wb') as ff:
            with open('log.txt', 'w') as log:
                consecutive_fails = 0
                count = 0
                for l in list:
                    if consecutive_fails < 100:
                        count += 1
                        print count
                        #time.sleep(random.uniform(0,2))
                        try:
                            fight_history, meta = build_fight_history(l)
                            consecutive_fails = 0
                        except:
                            consecutive_fails += 1
                            print consecutive_fails
                            continue
                        wtr = csv.writer(f, delimiter= ',')
                        wtr.writerows(fight_history)
                        wtr_meta = csv.writer(ff, delimiter= ',')
                        wtr_meta.writerow(meta)
                        log.write('%s\n' % l)
                    else:
                        break

def main(argv):
    list = range(int(argv[1]), int(argv[2]), 1)
    random.shuffle(list)
    output_database = argv[3]
    output_metadata = argv[4]
    build_database(list, output_database, output_metadata)

if __name__ == '__main__':
    main(sys.argv)

