import context
import dom

homepage = dom.HtmlPage('https://info.cern.ch/hypertext/WWW/TheProject.html')

if __name__ == '__main__':
    c1 = context.Conductor('context1', [homepage])
