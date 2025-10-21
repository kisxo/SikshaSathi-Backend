# Anganwadi app flow 
## 1.App opens to login page
- send json `{"id" : "string", "password": "string"}`
  - if ( admin )
    - go to admin dashboard
  - else if ( supervisor )
    - go to supervisor dashboard
  -  else if ( anganwadi )
     - go to anganwadi center dashboard

## 2.After login

### Admin dashboard 
  #### TODO

### Supervisor dashboard
- List centers -> centers page

    #### Centers page
    - Table of allotted centers -> center detail[id] page

### Anganwadi dashboard
- Attendance button -> attendance page
- Center details -> center detail page
- Student details -> student detail page

    #### Attendance page
    - Attendance > List all attendance
    - Student button > send student picture [?type=student]
    - Worker button > send worker picture [?type=worker]
    - Helper button > send helper picture [?type=helper]