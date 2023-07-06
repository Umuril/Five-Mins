# Knock-Knock
## Connecting People in Need with Available Help

Knock-Knock is a website dedicated to fostering a supportive community by connecting individuals in need of assistance with those who have available free time. Our platform allows people to find help when they need it most.

### Website Features
Most features are available to registered users.  
As a guest, you can browse Knock-Knocks to see other users' requests.  
Upon registration, you can create new requests and submit them to help other users, sometimes with something in return.  

### How to test locally
Just run:
```bash
./startup.sh
```

### Technology Used
- Framework: Django
- Database: SQLite3

### Project Goals
- [x] Guests can view the latest updated Knock-Knocks to see other users' activities and be encouraged to register.
- [x] Guests can search for requests based on title, day and/or category.
- [x] Users can create new assistance requests called Knock-Knock.
- [x] Users can view their homepage, which displays their current active Knock-Knocks, the Knock-Knocks they are trying to apply for, and a list of possible new works to apply for.
- [x] Users can communicate via an internal chat to coordinate before, during, and after a match is made.
- [x] The admin can generate random data for testing purposes using CLI commands.
- [x] Determine the flow for matching Users.
- [x] Implement a rating system where Users can rate each other based on the quality of work done.

### Pending Decisions
- [ ] Allowing multiple workers to work on a single Knock-Knock.
- [ ] Enabling workers to set their default availability time.

### Roles
- Guest (Not logged-in user)
- User (Logged-in user)
- Visibility-Narrowed (Logged-in users who are interested in free or paid works)
- Admin (Website administrator)

### Screenshot
<img src="https://github.com/Umuril/Knock-Knock/assets/3881068/70718594-d16f-49c0-8ef9-75d95d319974" width="200">
<img src="https://github.com/Umuril/Knock-Knock/assets/3881068/6a8acf65-0710-4a37-93de-f9d673042e66" width="200">
<img src="https://github.com/Umuril/Knock-Knock/assets/3881068/986630d1-dc7c-47f4-913d-33a2dfc92997" width="200">
<img src="https://github.com/Umuril/Knock-Knock/assets/3881068/33a39326-8dd8-46cd-a0d4-2a3f985eaf8d" width="200">
