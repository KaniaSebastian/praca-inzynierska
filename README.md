# Zapunktuj - Peer Assessment Web App

This web application was created as part of an engineering thesis and refined as part of a master's thesis. 

**Its main purpose is to allow students to upload their projects and perform peer reviews.**

This application allows its administrator (a teacher) to create groups of several students, whose task is to complete a project within one of the academic subjects. Such works are then posted on the Zapunktuj platform within a specified deadline. Then, students have an opportunity to evaluate their peers. 
The app randomly selects one of three different assessment methods (for later comparison) allowing students to award points, add comments regarding strong and weak aspects of a work and distinct best/favourite projects.
After completing the assessment, students can see how many points their work received and see the ranking of all works completed by a given group. Then it is possible to perform a second assessment phase so students are able to improve their projects based on the feedback received. The teacher is also able to assess projects and leave written feedback. 

**This application was hosted and used in practice multiple times.** This made it possible to test it and collect data for analysis.
Since January 2020, six student groups have used the Zapunktuj app to conduct college evaluations. The first three of them performed the assessment using the original version of the app, scoring only one way. These groups uploaded a total of 51 projects, which were scored by 118 people. The other three student groups made their assessments after making changes to the app that introduced additional evaluation methods. They uploaded 91 projects to the app, which were evaluated by 200 people. **A total of 318 students used Zapunktuj, uploading a total of 142 projects.** This compilation omits two groups that uploaded projects but did not conduct a peer review.
Students were also provided with instructions describing how to use the application and were encouraged to submit any comments on an ongoing basis by sending a message to a dedicated e-mail address.

Zapunktuj has a feature to switch between English and Polish version based on the web browser language settings. 
It was made using MVC pattern. It's responsive and cross-platform. 
It has a super-user that is able to add more administrators (teachers) that have limited access only to groups created by them. 
When a group is created, adnim is able to download and send access codes to studets so they can log in.
Students do projects in subsections (1:N students per section) but complete the assessment individually.

## Details
- Backend - Python 3.7
- Web Framework - Flask
- Frontend - Bootstrap 4.3.1
- Database - SQLite
- ORM - SQLAlchemy
- Translations - Babel

**Detailed technical and user documentation available uppon request.**

