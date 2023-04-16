echo 'Creating application user and database...'
mongosh ${DATABASE_NAME} \
  --host localhost \
  --port ${DATABASE_PORT} \
  -u ${MONGO_INITDB_ROOT_USERNAME} \
  -p ${MONGO_INITDB_ROOT_PASSWORD} \
  --authenticationDatabase admin \
  --eval "db.createUser({user: '${DATABASE_USERNAME}', pwd: '${DATABASE_PASSWORD}', roles:[{role:'dbOwner', db: '${DATABASE_NAME}'}]});"