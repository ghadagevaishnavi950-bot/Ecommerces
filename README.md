# Mini E-Commerce Web Application

A Flask-based mini e-commerce web application supporting three user roles: Customer, Seller, and Admin.

ECOMMERCE_APP/
│── app.py
│── requirements.txt
│── data_new.xlsx # optional Excel DB
│── ecommerce.db # optional SQLite DB
│
├── routes/
│ ├── users/
│ │ └── users.py
│ ├── products/
│ │ └── products.py
│ └── orders/
│ └── orders.py
│
├── templates/
│ ├── users/
│ │ ├── register.html
│ │ ├── login.html
│ │ └── dashboard.html
│ ├── products/
│ │ └── products.html
│ └── orders/
│ └── orders.html
│
└── static/ # CSS/JS files (optional)


## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/<username>/ECOMMERCE.git
cd ECOMMERCE


Install dependencies:

pip install -r requirements.txt


Setup the database:

SQLite (recommended): Create ecommerce.db using the provided schema.
