# -*- coding: utf-8 -*-
{
    'name': "Odoo Test",

    'summary': """
        Odoo Engineering skill test by eFishery""",

    'description': """
        ● User Module
            1. Web Odoo mamapu membuat user baru dengan cara import, jumlah
            item yang di import dapat berjumlah ratusan atau lebih item sekaligus.
                ■ Proses berjalan secara background, tanpa harus aktor menunggu.
                ■ Aktor dapat mengtahui status background proses.
                ■ Aktor akan mendapat notifikasi jika background proses telah
                selesai (Nice to have).

        ● Auth Module
            1. Satu endpoint untuk login lalu mengembalikan JWT dengan isi private
            claims email, role .
            2. Web Odoo mempunyai caapability untuk membatasi active login user
            hanya pada satu tab browser/device(piliah salah satu). (Very nice to
            have)
        ● Fetch Module
            1. Satu endpoint fetch dari resources
                ■ resource:
                https://stein.efishery.com/v1/storages/5e1edf521073e315924ceab
                4/list
                ■ tambahkan field baru untuk price dalam USD(price asli dalam IDR)
                dengan menggunakan layanan currency converter (misal:
                https://free.currencyconverterapi.com). Coba pikirkan caching
                untuk menambah performance tiap request.
                ■ Role admin request tidak ada batasan brust/average request,
                sedangkan role selain admin request di batasi brust/average 1 req
                per 2 detik. (Very nice to have)
                ■ Menampilkan balikkan yang sesuai apabila JWT Token tidak valid.

        ● Marketplace Module
            1. Satu endpoint untuk melakukan transaksi order hingga pembayaran
                ■ Sale order terbuat dengan state confirmed.
                ■ Invoice terbuat dengan state posted.
                ■ Payment registered dengan status invoice in payment.
                ■ Menampilkan balikkan yang sesuai apabila JWT Token tidak valid.
            2. Satu endpoint fetch list sale order
                ■ Menampilkan balikan list sale order yang telah di buat
                ■ Akses ke database menggunakan slave connection (Very nice to
                have)
                ■ Menampilkan balikkan yang sesuai apabila JWT Token tidak valid.
    """,

    'author': "Kams",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web_notify'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/import_views.xml',
        'wizard/import_views.xml',
        'views/auth_views.xml',
    ],
}
