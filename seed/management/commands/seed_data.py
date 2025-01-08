from django.core.management.base import BaseCommand
from automation.models import Contact, MessageLog
from faker import Faker
import random

class Command(BaseCommand):
    help = "Seeds the database with sample data"

    def handle(self, *args, **kwargs):
        faker = Faker()

        # Create Contacts
        for _ in range(50):
            Contact.objects.create(
                full_name=faker.name(),
                phone_number=faker.phone_number(),
                email=faker.email(),
                country_code=f"+{random.randint(1, 300)}",
            )

        # Create Message Logs
        contacts = Contact.objects.all()
        for contact in contacts:
            for _ in range(random.randint(1, 5)):
                MessageLog.objects.create(
                    contact=contact,
                    message_content=faker.sentence(),
                    is_response=random.choice([True, False]),
                )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))