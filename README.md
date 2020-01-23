# Jimmy Westerlund 39053

The following use cases are implemented:
- UC1: Create a user account
- UC2: Edit account information 
- UC3: Create a new auction 
- UC4: Edit the description of an auction 
- UC5: Browse and search auctions 
- UC6: Bid 
- UC7: Ban an auction 
- UC8: Resolve auction 
- UC9: Support for multiple languages 
- UC10: Support Multiple Concurrent Sessions 
- REQ9.3: Store language preferences
- REQ3.5: Send seller auction link
- WS1: Browse & Search API

The automated test "testTDD" fails on UC3 and forward, but I have followed
the requirements and performed manual tests to ensure each use case should meet the requirements. Test for UC9 fails because it expects status code 200
but I could not figure out how to do it without a redirect (code 302). 

Chrome was used testing the application.


## Packages used

Django==2.2.5

requests==2.22.0

djangorestframework==3.10.2

freezegun==0.3.12

django-optimistic-lock==1.0.0

markdown==3.1.1




