# ELearning
![Flask](https://img.shields.io/badge/Flask-0.12.2-red.svg)  ![Updating](https://img.shields.io/badge/Project-updating-brightgreen.svg)

** A simple e-learning backend **

So many things here need to be improved, like route schema and security strategy.

But it's a not bad beginning.

If you meet questions when you read this program, you are welcome to contact with me by Wechat: smartseer.

: )

## Structure
note: there are some prepared files in static and templates folder to make a simple view.
- auth/
  - register
  - login(different roles, google+)
  - logout
  - generate tencent cos signature
- cos/(course)
  - display course
  - view course information
  - add or get notes
  - view course posts
  - read or write post
  - add or get comments
  - upload course(file) to tencent cos
  - activate or deactivate a course
  - set course picture
- main/
  - index
  - show course list
  - show school list
  - show teacher list
- pay/
  - show course(goods) info
  - create a payment
  - execute a payment
  - show pay result
  - get or add courses of cart
  - get or bind coupon
  - (user can buy course for another user)
- per/(person)
  - view user information(owner or guest)
  - bind gmail
  - change posts user liked
  - send message to another user
  - tip new message
  - get new messages
  - bind parent only when user's role is student
  - show user's child(childern) only when user's role is parent
  - show user's order
  - set user avatar
- sch/(school)
  - apply to join in a existed school only when user's role is teacher
  - apply to create a new school only when user's role is administrator
  - accept a teacher as own school member
  - show orders
  - set school picture
- tests/
  - test some not all functions
- \_\_init__.py
  - salted session implementation
  - create Flask app
- basic.py/
  - offer some basic opertions
- db.py/
  - offer mysql and redis connection
- models.py/
  - ORM model
  - fake data
  - refresh database(drop tables and then create them, end with fake data filled)
- manager.py/
  - start the project
  - some addtional opertions

## Waiting to do
  - contact operations
  - route optimization
  - improve paypal process
  - improve google+ login process

## Change log
  - add the test module and fix some details
  - add a salted session choice
  - add a simple pagination
