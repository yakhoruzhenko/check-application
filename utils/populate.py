import random
from datetime import datetime, timedelta
from decimal import Decimal

from app.infra.database import session_scope
from app.infra.enums import PaymentMethod
from app.models.checks import Check, Item
from app.models.users import User
from app.services.hashing import Hash

NUM_USERS = 10  # Number of dummy users to generate
NUM_CHECKS = 100  # Number of dummy checks to generate for each user
NUM_ITEMS = 5  # Number of dummy items per check
DATE_START = datetime(2025, 2, 1, random.randint(0, 23), random.randint(0, 59), random.randint(0, 59))
DATE_END = datetime(2025, 4, 1, random.randint(0, 23), random.randint(0, 59), random.randint(0, 59))
NAME_PREFIXES = [
    "Premium", "Deluxe", "Eco", "Smart", "Advanced", "Compact", "Luxury", "Portable", "Innovative", "Exclusive",
    "Classic", "Modern", "Ergonomic", "Stylish", "Sustainable", "Comfortable", "High-end", "Durable", "Heavy-duty",
    "Professional", "Affordable", "Sleek", "Cutting-edge", "Trendy", "Space-saving", "Functional", "Eco-friendly",
    "Foldable", "Multifunctional", "Water-resistant", "High-quality", "Fast-charging", "User-friendly", "Secure",
    "Intuitive", "Precision", "High-performance", "Top-tier", "Weatherproof", "All-season", "Multitasking", "Vegan",
    "Ultra-light", "Recyclable", "Multi-purpose", "Quick-dry", "Temperature-resistant", "Weather-resistant",
    "Anti-slip", "Long-lasting", "Low-maintenance", "Colorful", "Vibrant", "Elegant", "Chic", "Stackable",
    "Energy-efficient", "Travel-friendly", "Multicolor", "Quiet", "Adjustable", "Flexible", "Industrial", "Mobile",
    "Hygienic", "Biodegradable", "Customizable", "Futuristic", "Vintage", "Handmade", "Custom"
]
NOUNS = ["Enterprises", "Solutions", "Industries", "Innovations", "Products", "Systems", "Creations", "Ventures",
         "Concepts", "Holdings"]
COMPANY_TYPES = ["LLC", "Corp.", "Inc.", "GmbH", "S.A.", "Co.", "LLP", "PLC", "B.V.", "AG"]
COMPANY_NAME_COMPONENTS = (NAME_PREFIXES, NOUNS, COMPANY_TYPES)


def populate_data(num_users: int = NUM_USERS, num_checks: int = NUM_CHECKS, num_items: int = NUM_ITEMS,
                  date_start: datetime = DATE_START, date_end: datetime = DATE_END,
                  company_name_components: tuple[list[str], list[str], list[str]] = COMPANY_NAME_COMPONENTS
                  ) -> None:
    name_prefixes, nouns, company_types = company_name_components
    with session_scope() as session:
        # Generate Users
        users = []
        for i in range(num_users):
            prefix = ' '.join(random.sample(name_prefixes, random.randint(1, 3)))
            user = User(
                name=f'{prefix} {random.choice(nouns)} {random.randint(10, 2100)} {random.choice(company_types)}',
                login=f'user{i + 1}',
                email=f'user{i + 1}@example.com',
                password=Hash.bcrypt('password123')
            )
            users.append(user)
        session.add_all(users)
        session.flush()

        # Generate Checks and Items for each User
        items = []
        for user in users:
            session.refresh(user)
            for _ in range(num_checks):
                check = Check(
                    creator_id=user.id,
                    payment_method=random.choice(list(PaymentMethod)),
                    paid_amount=Decimal(random.randint(10000, 50000)) / Decimal(100),
                    created_at=random.choice(
                        [date_start + timedelta(days=i) for i in range((date_end - date_start).days)]
                    ))
                session.add(check)
                session.flush()
                session.refresh(check)

                # Generate Items for each Check
                for _ in range(num_items):
                    title = ' '.join(random.sample(name_prefixes, random.randint(3, 10)))
                    item = Item(
                        check_id=check.id,
                        title=f'{title} Item',
                        price=Decimal(random.randint(1000, 10000)) / Decimal(100),
                        quantity=random.randint(1, 10),
                    )
                    items.append(item)

        session.add_all(items)
        session.commit()

    print(f'Inserted {num_users} users and {num_users * num_checks} checks into the DB')


if __name__ == '__main__':
    populate_data()
