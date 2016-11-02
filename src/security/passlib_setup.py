#
# Contains setup for passlib password hashing
#
from passlib.context import CryptContext

pwd_context = CryptContext(
    # List of hash(es) you wish to support.
    schemes=["bcrypt","pbkdf2_sha512"],
    default="bcrypt",

    # vary rounds parameter randomly when creating new hashes...
    all__vary_rounds = 0.1,

    # set the number of rounds that should be used...
    # (appropriate values may vary for different schemes,
    # and the amount of time you wish it to take)
    bcrypt__default_rounds = 8,
    pbkdf2_sha512__default_rounds = 4000,
    )
