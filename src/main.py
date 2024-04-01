import conductor
import collaborator

if __name__ == '__main__':
    c1 = conductor.Conductor('context1', 'http://localhost:8000/testPage.html')
    c2 = collaborator.Collaborator('Collaborator', 'localhost', 10000)
