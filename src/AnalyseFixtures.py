import sys
import smtplib
from Logging import Logger
from FootyUtils import getFootyOptions, getFootyConfig, newCSVFile, \
        readCSVFileAsDict
from FootyAnalysisTools import model, analysisDir

def fSD(d):
    '''
    Format string of result data - freqency, percentage, odds
    '''
    return '({:>4d} {:>6.2f}% {:>5.2f})'.format(d[0], d[1], d[2])

def fST(d):
    '''
    Format string of results titles - #, %, odds
    '''
    return '({:<4s} {:<7s} {:<5s})'.format(d[0], d[1], d[2])

def hl(s):
    '''
    Higlight the string
    '''
    return '\033[1m' + s + '\033[0m'

def mail_hl(s):
    '''
    Highlight the string for email output
    '''
    s = s.replace('<td>', '<td bgcolor="yellow">')
    s = s.replace(
            '<td align="right">', '<td align="right" bgcolor="yellow">')
    return s

def analyseFixtures(resultsURLTmpl, fixturesURL, opts=sys.argv):
    log = Logger()
    (sendMail, rangeMap) = getFootyOptions(log, opts) 
    (algoCfg, mailCfg) = getFootyConfig()
    rangeMap = algoCfg['rangeMap']
    season = algoCfg['season']
    teamErrorMap = algoCfg['teamErrorMap']

    mailText = '<table border=1><tr><th>Lge</th><th>Date</th><th>HomeTeam</th><th>AwayTeam</th><th>Mark</th><th>H#</th><th>H%</th><th>H Odds</th><th>HomeTeamForm</th><th>AwayTeamForm</th></tr>'
    s = '{:<4s} {:<8s} {:<16s} {:<16s} {:<4s} {:s} {:<37s} {:<37s}'.format(
            'Lge', 'Date', 'HomeTeam', 'AwayTeam', 'Mark', 
            fST(('H#','H%', 'HO')), 'HomeTeamForm', 'AwayTeamForm')
    termText = '\n' + hl(s) + '\n'

    with newCSVFile(
            '{}/Betting.{}.csv'.format(analysisDir, model.__class__.__name__),
            ['Lge', 'Date', 'HomeTeam', 'AwayTeam', 'Mark', 'H#', 'H%', 
                'HOdds', 'HomeTeamForm', 'AwayTeamForm']) as bettingWriter:
        league = ''
        data = {}
        summaryData = {}
        with readCSVFileAsDict(fixturesURL) as fixturesReader:
            for fix in fixturesReader:
                log.debug(fix)
                ind = 'b\"Div'
                try:
                    fix['b\"Div']
                except:
                    ind = 'b\'Div'
                    
                if fix[ind] not in rangeMap:
                    continue
                if league != fix[ind]:
                    league = fix[ind]
                    resultsURL = resultsURLTmpl.format(season, league)
                    log.info(resultsURL)
                    with readCSVFileAsDict(resultsURL) as resultsReader:
                        data = model.processMatches(resultsReader)
                        with readCSVFileAsDict(
                                '{}/{}/Summary.{}.csv'.format(analysisDir,
                                    league, model.__class__.__name__)) \
                                            as summaryReader:
                            for summ in summaryReader:
                                mark = int(summ['Mark'])
                                f = int(summ['Frequency'])
                                hP = float(summ['%H'])
                                dP = float(summ['%D'])
                                aP = float(summ['%A'])
                                summaryData[mark] = {
                                        'H' : (int(f * (hP / 100)), 
                                            float(summ['%H']), 
                                            float(summ['HO'])),
                                        'D' : (int(f * (dP / 100)), 
                                            float(summ['%D']), 
                                            float(summ['DO'])),
                                        'A' : (int(f * (aP / 100)), 
                                            float(summ['%A']), 
                                            float(summ['AO']))}
                ht = fix['HomeTeam']
                if ht in teamErrorMap:
                    ht = teamErrorMap[ht]
                at = fix['AwayTeam']
                if at in teamErrorMap:
                    at = teamErrorMap[at]
                date, ht, at, mark, hForm, aForm = model.markMatch(
                        data, fix['Date'], ht, at)
                if mark is None or mark not in range(-15, 16):
                    continue
                hSD = summaryData[mark]['H'] 
                aSD = summaryData[mark]['A'] 
                dSD = summaryData[mark]['D'] 

                s = '{:<4s} {:<8s} {:<16s} {:<16s} {:4d} {:s} ({:s}) ({:s})'\
                        .format(league, date, ht, at, mark, fSD(hSD), 
                                hForm, aForm)
                mail_s = '<tr><td>{:s}</td><td>{:s}</td><td>{:s}</td><td>{:s}</td><td align="right">{:>4d}</td><td align="right">{:>4d}</td><td align="right">{:>6.2f}%</td><td align="right">{:>5.2f}</td><td align="right">{:s}</td><td align="right">{:s}</td></tr>'.format(
                        league, date, ht, at, mark, hSD[0], hSD[1], hSD[2], 
                        hForm, aForm)
                if mark in rangeMap[league]:
                    termText += hl(s) + '\n'
                    mailText += mail_hl(mail_s)
                else:
                    termText += s + '\n'
                    mailText += mail_s
                bettingWriter.writerow(
                        (league, date, ht, at, mark, hSD[0], hSD[1], hSD[2], 
                            hForm, aForm))

    log.info(termText)
    mailText += '</table>'
    mailText = 'MIME-Version: 1.0\nContent-type: text/html\nSubject: Footy Bets\n\n{}'.format(mailText)

    if sendMail:
        fromAddr = mailCfg['fromAddr']
        toAddrs = mailCfg['toAddrs']
        server = smtplib.SMTP(mailCfg['svr'], int(mailCfg['port']))
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(fromAddr, mailCfg['pwd'])
        server.sendmail(fromAddr, toAddrs, mailText)
        server.quit()
        log.info('email sent to: {!s}'.format(toAddrs))

if __name__ == '__main__':
    '''
     How often do the following urls change?
    '''
    resultsURLTmpl = 'http://www.football-data.co.uk/mmz4281/{}/{}.csv'
    fixturesURL = 'http://www.football-data.co.uk/fixtures.csv'
    #fixturesURL = 'file:///home/mckone/Documents/Stuff/Footy/fixtures.txt'

    analyseFixtures(resultURLTmpl, fixturesURL, sys.argv)
