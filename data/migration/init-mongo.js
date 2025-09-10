// MongoDB initialization script

// Use default values since process.env is not available in MongoDB shell
const dbName = 'stock_assistant';
const username = 'stockadmin';
const password = 'stockpassword';

// Connect to MongoDB
db = db.getSiblingDB(dbName);

// Create user for this database with necessary permissions
try {
    // Check if user already exists
    const users = db.getUsers();
    const userExists = users.some(user => user.user === username);
    
    if (!userExists) {
        db.createUser({
            user: username,
            pwd: password,
            roles: [
                { role: 'readWrite', db: dbName },
                { role: 'dbAdmin', db: dbName }  // Added for schema management
            ]
        });
        print('Created user for database: ' + dbName + ' with readWrite and dbAdmin roles');
    } else {
        print('User already exists for database: ' + dbName);
        
        // Update user roles if necessary
        const existingUser = users.find(user => user.user === username);
        const hasDbAdmin = existingUser.roles.some(role => 
            role.role === 'dbAdmin' && role.db === dbName
        );
        
        if (!hasDbAdmin) {
            db.updateUser(username, {
                roles: [
                    { role: 'readWrite', db: dbName },
                    { role: 'dbAdmin', db: dbName }
                ]
            });
            print('Updated user roles to include dbAdmin');
        }
    }
} catch (error) {
    print('Error creating/updating user: ' + error);
}