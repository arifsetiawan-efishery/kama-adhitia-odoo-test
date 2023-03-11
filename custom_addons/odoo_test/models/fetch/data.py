# -*- coding: utf-8 -*-

from odoo import models, fields
import requests


class FetchCache(models.Model):

    _name = 'kams.cache.data'
    _description = "Cache Data"

    name = fields.Text('Data')

    def fetch_data(self):
        url = "https://stein.efishery.com/v1/storages/5e1edf521073e315924ceab4/list"
        try:
            old_data = self.env['kams.cache.data'].search([])
            if old_data:
                for old in old_data:
                    old.unlink()

            res = requests.request("GET", url)
            response = res.json()
            rate = self.env['ir.config_parameter'].get_param(
                'currency_rate_idr_to_usd', '1')
            for list in response:
                usd_price = float(list.get('price')) / float(rate)
                insert_price = {"usd_price": str(round(usd_price, 3))}
                list.update(insert_price)
                self.env['kams.cache.data'].create({
                    "name": str(list)
                })
        except:
            pass

    def get_currency_rate(self):

        url = "https://api.apilayer.com/currency_data/convert?to=IDR&from=USD&amount=1"
        headers = {
            'apikey': '327jisVHnJJXxpT4hX5hGdpa5kQXlSEj'
        }
        try:
            res = requests.request("GET", url, headers=headers)
            response = res.json()

            rate = response.get('result', 1)

            self.env['ir.config_parameter'].set_param(
                'currency_rate_idr_to_usd', rate)
        except:
            pass
