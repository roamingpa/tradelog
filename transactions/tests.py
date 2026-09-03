from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from catalog.models import Card
from contacts.models import Contact
from transactions.models import Purchase, PurchaseItem, Sale, SaleItem
from transactions.whatsapp_parser import parse_whatsapp_import


class WhatsappImportParserTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(username='luis')
		self.card = Card.objects.create(code='OP01-001', name='Monkey D. Luffy')
		self.contact = Contact.objects.create(owner=self.user, name='Juan Perez', whatsapp='+56 9 1234 5678')

	def parse(self, text):
		return parse_whatsapp_import(
			text,
			transaction_kind='purchase',
			cards=Card.objects.all(),
			contacts=Contact.objects.filter(owner=self.user),
			own_names=['Luis', self.user.username],
		)

	def test_detects_contact_card_quantity_price_and_shipping(self):
		result = self.parse(
			'03/09/2026, 10:14 - Juan Perez: Hola, tengo 2x OP01-001 a $3.000 c/u\n'
			'03/09/2026, 10:15 - Luis: perfecto, me lo puedes mandar por envio?'
		)

		self.assertTrue(result['looks_like_chat'])
		self.assertEqual(result['contact']['id'], str(self.contact.pk))
		self.assertEqual(result['items'][0]['card_id'], str(self.card.pk))
		self.assertEqual(result['items'][0]['quantity'], 2)
		self.assertEqual(result['items'][0]['unit_price'], '3000')
		self.assertIs(result['is_shipping'], True)

	def test_reports_unmatched_card_codes(self):
		result = self.parse('Juan: tienes EB01-999 por 3k?')

		self.assertEqual(result['items'][0]['code'], 'EB01-999')
		self.assertFalse(result['items'][0]['matched'])
		self.assertEqual(result['unmatched_codes'], ['EB01-999'])

	def test_accepts_raw_speaker_lines_and_short_set_codes(self):
		result = self.parse('Juan Perez: me queda OP1-001 $3000')

		self.assertTrue(result['looks_like_chat'])
		self.assertEqual(result['contact']['id'], str(self.contact.pk))
		self.assertEqual(result['items'][0]['code'], 'OP01-001')
		self.assertEqual(result['items'][0]['card_id'], str(self.card.pk))

	def test_detects_currency_merges_duplicates_and_splits_total_price(self):
		result = self.parse('Juan Perez: 2x OP01-001 total $6.000 CLP\nJuan Perez: OP01-001 $3.000')

		self.assertEqual(result['currency'], 'CLP')
		self.assertEqual(len(result['items']), 1)
		self.assertEqual(result['items'][0]['quantity'], 3)
		self.assertEqual(result['items'][0]['unit_price'], '3000')
		self.assertTrue(result['items'][0]['card_image_url'])


class WhatsappImportViewTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(username='luis', password='pass')
		self.card = Card.objects.create(code='OP01-001', name='Monkey D. Luffy')
		self.contact = Contact.objects.create(owner=self.user, name='Juan Perez')
		self.client.force_login(self.user)

	def test_preview_endpoint_returns_detected_items(self):
		response = self.client.post(
			reverse('whatsapp-import-preview', args=['sale']),
			{'text': 'Juan Perez: OP01-001 $3000'},
		)

		self.assertEqual(response.status_code, 200)
		data = response.json()
		self.assertEqual(data['contact']['id'], str(self.contact.pk))
		self.assertEqual(data['items'][0]['card_id'], str(self.card.pk))

	def test_new_purchase_form_renders_whatsapp_import_panel(self):
		response = self.client.get(reverse('purchase-new'))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Importar desde WhatsApp')


class TransactionUxViewTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(username='luis', password='pass')
		self.card = Card.objects.create(code='OP01-001', name='Monkey D. Luffy')
		self.contact = Contact.objects.create(owner=self.user, name='Juan Perez')
		self.purchase = Purchase.objects.create(owner=self.user, date='2026-09-03', seller=self.contact)
		self.purchase_item = PurchaseItem.objects.create(purchase=self.purchase, card=self.card, is_found=False)
		self.sale = Sale.objects.create(owner=self.user, date='2026-09-03', buyer=self.contact, is_shipping=True)
		self.sale_item = SaleItem.objects.create(sale=self.sale, card=self.card, is_found=False)
		self.client.force_login(self.user)

	def test_purchase_list_filters_by_status_and_query(self):
		response = self.client.get(reverse('purchase-list'), {'status': 'pending', 'q': 'Luffy'})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Juan Perez')
		self.assertContains(response, 'value="Luffy"')

	def test_purchase_mark_all_found_updates_items(self):
		response = self.client.post(reverse('purchase-items-mark-all-found', args=[self.purchase.pk]))

		self.assertEqual(response.status_code, 200)
		self.purchase_item.refresh_from_db()
		self.assertTrue(self.purchase_item.is_found)

	def test_sale_mark_all_found_updates_items(self):
		response = self.client.post(reverse('sale-items-mark-all-found', args=[self.sale.pk]))

		self.assertEqual(response.status_code, 200)
		self.sale_item.refresh_from_db()
		self.assertTrue(self.sale_item.is_found)
