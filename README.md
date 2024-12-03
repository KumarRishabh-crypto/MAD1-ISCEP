# InflueSync App

## Description
InflueSync is a cutting-edge platform designed to revolutionize the way brands connect with influencers. By providing a seamless interface for managing influencer collaborations and sponsorship programs, InflueSync enables brands to effortlessly coordinate campaigns, track performance, and maximize their reach. Our platform offers robust tools for both sponsors and influencers, ensuring transparent communication, efficient project management, and measurable results. With InflueSync, creating impactful partnerships and driving brand success has never been easier.
Here user can:
- Register and log in
- Browse available services
- Make requests

The system also includes an admin panel for managing campaigns and user roles.

## Screenshots

[![Screenshot 2024-12-03 20224525](https://github.com/KumarRishabh-crypto/MAD1-ISCEP/blob/main/Screenshot%202024-12-03%20224525.png)

## Technologies Used

- **Flask**: A simple and extensible micro web framework in Python.
- **Jinja2**: A templating engine for generating dynamic HTML content.
- **SQLAlchemy**: An ORM library for database management.
- **SQLite**: A lightweight relational database management system.
- **Bootstrap**: A frontend framework for creating a responsive and appealing user interface.
- **Flask-Login**: an extension of Flask, used for the user session management. Logging in and out, remembering the user, storing active user data etc are handled 
with this extension.

## Database Schema Design

**Users**: user_id (Primary Key), username, password, role, status.
**SponsorInformation**: user_id (Primary Key, Foreign Key from Users), email, industry, brand.
**InfluencerInformation**: user_id (Primary Key, Foreign Key from Users), email, category, niche, reach.
**Campaign**: campaign_id (Primary Key), sponsor_id (Foreign Key from Users), name, budget, sdate, edate, goal, category, bio.
**Request**: influencer_id (Primary Key, Foreign Key from Users), sponsor_id (Primary Key, Foreign Key from Users), campaign_id (Primary Key, Foreign Key from Campaign), status, requestor.

## Architecture and Features
The project uses the MVC (Model-View-Controller) architecture:

- **Controllers**: Manage the routes and business logic.
- **Templates**: HTML files with Jinja2 for the presentation layer.
- **Models**: Represent the database tables.

### Key Features

**1. The flask app** opens at the main page. Where person can
i.User login: username and password are required fields in form. User should exist in the database or he/she can register himself/herself.
ii.Admin login: username and password are required fields in form. Admin cannot register, id is created at the start itself.
iii.Register user: first name, username and password are required in form.
Username should not exist in the database.
If incorrect password or username is given a prompt is displayed invalid credentials.

**2. Users**
a. Sponsor:
● Can login and create campaigns, update it, delete campaigns.
● Search for influencers and send Ad-request influencers to participate in their respective campaigns.
● They can accept of reject request sent by influencers to participate in campaigns.
b. Influencer:
● Can login, update their profile.
● An influencer will handle ad requests by accepting or rejecting them, and they can send revised ad requests back to sponsors.
● They can also search for active campaigns based on criteria like name and category and choose to participate. Additionally, they can delete their requests.
c. Admin:
● Can login, and see all the statistics in dashboard.
● An admin can monitor all the users/campaigns,
● Admin have ability to flag inappropriate campaigns/users, and also view and delete it.

This README file provides an overview of the InflueSync App, its technologies, database schema, and main features. It is designed to help users and collaborators understand the project's structure and functionality.
