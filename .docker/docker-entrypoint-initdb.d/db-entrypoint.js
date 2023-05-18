db.getSiblingDB('admin').auth(
  process.env['MONGO_INITDB_ROOT_USERNAME'], 
  process.env['MONGO_INITDB_ROOT_PASSWORD']
);

db.createUser({
user: process.env['DATABASE_USERNAME'],
pwd: process.env['DATABASE_PASSWORD'],
roles: [
  {
    role: 'dbOwner',
    db: process.env['DATABASE_NAME'],
  },
],
});
