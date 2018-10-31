import csv
import lxml.html
import requests

schedule = {}

with open('schedule.csv', 'w') as csv_out:
    headers = ['start', 'end', 'location', 'title', 'level', 'speaker', 'timing']
    csv_writer = csv.DictWriter(csv_out, headers)
    csv_writer.writeheader()

    for day in [7,8,9]:
        page = requests.get('https://2018.ploneconf.org/schedule/talks-november-%s' % day)
        doc = lxml.html.fromstring(page.content)
        div = doc.get_element_by_id('parent-fieldname-text')
        table = div[1]
        thead = table[0]
        tr = thead[0]

        locations = []
        # Skip the first column
        for td in tr[1:]:
            locations.append(td.text)

        tbody = thead.getnext()
        for tr in tbody:
            th = tr[0]
            row = {n: '' for n in headers}
            row['start'], row['end'] = th.text.split(' - ')
            count = 0
            for td in tr.iter('td'):

                h4 = td.find('h4')
                if h4 is None:
                    h2 = td.find('h2')
                    if h2 is None:
                        # Blank cell
                        continue
                    else:
                        row['title'] = h2.text
                else:
                    row['title'] = h4.text

                row['location'] = locations[count]
                count += 1

                p = td.find('p')
                if p is None:
                    continue
                if '/' in p.text:
                    row['speaker'], row['level'] = p.text.split(' / ')
                else:
                    if '(' in p.text:
                        row['speaker'], timing = p.text.split('(')
                        row['timing'] = timing[:-1]
                print(row)

                csv_writer.writerow(row)





