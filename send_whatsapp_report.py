import json
from pathlib import Path

from src.models.banana import Banana
from src.models.banana_sample import BananaSample
from src.models.banana_batch import BananaBatch

from src.repository.batch_repository import BatchRepository
from src.services.simulation_service import SimulationService
from src.services.report_service import ReportService
from src.services.notification_factory import NotificationFactory


# =====================
# LOAD BATCH
# =====================
repo = BatchRepository("data/results")
batch = repo.load_batch("Cavendish")

if len(batch) == 0:
    raise RuntimeError("No banana samples found. Run CV first.")

print(f"Loaded {len(batch)} samples")


# =====================
# USER INPUT
# =====================
quantity = int(input("\nEnter number of bananas to simulate: "))


# =====================
# SIMULATION
# =====================
simulation = SimulationService.simulate(batch, quantity)


# =====================
# BUILD REPORT
# =====================
report = ReportService.build_whatsapp_report(batch, simulation)

print("\n======= REPORT PREVIEW =======\n")
print(report)
print("\n==============================\n")


# =====================
# SEND NOTIFICATION
# =====================
notifier = NotificationFactory.create()
notifier.send(report)

print("✅ Report sent (or mocked)")
