from datetime import date
from sqlalchemy.orm import Session
from models import Payment, Contract
from database import SessionLocal


class PaymentService:
    def __init__(self):
        self.db = SessionLocal()

    def get_all_payments(self):
        return self.db.query(Payment).order_by(Payment.payment_date.desc()).all()

    def get_payment_by_id(self, payment_id):
        return self.db.query(Payment).filter(Payment.id == payment_id).first()

    def get_payments_by_contract(self, contract_id):
        return self.db.query(Payment).filter(
            Payment.contract_id == contract_id
        ).order_by(Payment.payment_date.desc()).all()

    def create_payment(self, payment_data):
        payment = Payment(
            contract_id=payment_data["contract_id"],
            payment_date=payment_data["payment_date"],
            amount=payment_data["amount"],
            payment_period_month=payment_data["payment_period_month"],
            payment_period_year=payment_data["payment_period_year"]
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def update_payment(self, payment_id, payment_data):
        payment = self.get_payment_by_id(payment_id)
        if payment:
            payment.contract_id = payment_data["contract_id"]
            payment.payment_date = payment_data["payment_date"]
            payment.amount = payment_data["amount"]
            payment.payment_period_month = payment_data["payment_period_month"]
            payment.payment_period_year = payment_data["payment_period_year"]
            self.db.commit()
            self.db.refresh(payment)
        return payment

    def delete_payment(self, payment_id):
        payment = self.get_payment_by_id(payment_id)
        if payment:
            self.db.delete(payment)
            self.db.commit()
            return True
        return False

    def get_total_payments_by_contract(self, contract_id):
        payments = self.get_payments_by_contract(contract_id)
        return sum(p.amount for p in payments)

    def get_payments_by_period(self, year, month):
        return self.db.query(Payment).filter(
            Payment.payment_period_year == year,
            Payment.payment_period_month == month
        ).all()

    def __del__(self):
        self.db.close()

    def get_overdue_contracts(self):
        from datetime import date, timedelta
        today = date.today()

        active_contracts = self.db.query(Contract).filter(Contract.status == "active").all()
        overdue_contracts = []

        for contract in active_contracts:
            last_payment = self.db.query(Payment).filter(
                Payment.contract_id == contract.id
            ).order_by(Payment.payment_period_year.desc(), Payment.payment_period_month.desc()).first()

            if last_payment:
                last_month = last_payment.payment_period_month
                last_year = last_payment.payment_period_year

                if last_month == 12:
                    next_month = 1
                    next_year = last_year + 1
                else:
                    next_month = last_month + 1
                    next_year = last_year

                if next_year < today.year or (next_year == today.year and next_month < today.month):
                    months_overdue = (today.year - next_year) * 12 + (today.month - next_month)
                    overdue_contracts.append({
                        "contract": contract,
                        "months_overdue": months_overdue,
                        "last_payment_date": last_payment.payment_date
                    })
            else:
                months_overdue = (today.year - contract.check_in_date.year) * 12 + (
                            today.month - contract.check_in_date.month)
                if months_overdue > 0:
                    overdue_contracts.append({
                        "contract": contract,
                        "months_overdue": months_overdue,
                        "last_payment_date": None
                    })

        return overdue_contracts

    def get_payments_report(self, start_date, end_date):
        payments = self.db.query(Payment).filter(
            Payment.payment_date >= start_date,
            Payment.payment_date <= end_date
        ).order_by(Payment.payment_date.desc()).all()

        total_amount = sum(p.amount for p in payments)

        return {
            "payments": payments,
            "total_amount": total_amount,
            "count": len(payments)
        }

    def get_payments_by_month(self, year, month):
        return self.get_payments_by_period(year, month)