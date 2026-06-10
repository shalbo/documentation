-- Dev default password for all seed users: Rousto@123

UPDATE users
SET password_hash = 'pbkdf2_sha256$100000$b9efcf9db61a5276c996ab3f3a823f68a178bd63299232f41a0ed435676b9b81'
WHERE password_hash IS NULL;
