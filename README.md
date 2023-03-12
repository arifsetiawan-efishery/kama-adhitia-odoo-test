# eFishery Odoo Test

# Outline

- Introduction
- Features
  - User Module
  - Auth Module
  - Fetch Module
  - Marketplace Module
- Buidling the server
  - Configuration detail
  - Build on Docker cointainer

# Introduction

This module is made to complete the task given to participate in the odoo developer selection at eFishery

# Features

## User Module

- Odoo Test -> Users -> Import

This function is used to bring up a pop up that is used to import the (`.csv`) file

- Odoo Test -> Users -> Import Process

This function is used to monitor the import process in the background

Processes that are currently running will be monitored in the logs. Logs can be opened by clicking the logs button on the running process form

After the import process is complete, the user will get a pop notification

- Odoo Test -> Users -> Import History

The completed import process will create a history containing the number of successful and failed import processes, log files, and the time the task was completed

## Auth Module

- Odoo Test -> Auth -> Configuration

To set the secret key

- Endpoint

Endpoint can be called at (`POST {host}/api/login`) by sending json data in the form of db_name, email, password

See the json collection in the repository for more details

## Fetch Module

Run the scheduler first in Settings(debug mode) -> Technical -> Scheduler Action -> "Get currency IDR to USD rate"

Then run the scheduler in Settings(debug mode) -> Technical -> Scheduler Action -> "Efishery Fetch Data"

- Odoo Test -> Fetch -> Cache Data

Json data that has been inserted in the usd currency based on prices obtained from efishery data

- Endpoint

Endpoint can be called at (`GET {host}/api/fetch`)

See the json collection in the repository for more details

## Marketplace Module

- Endpoint

Endpoint can be called at (`POST {host}/api/order`) to create an order

Endpoint can be called at (`GET {host}/api/order/list`) to view list created order

See the json collection in the repository for more details

# Building the server

## Configuration detail

- open (`docker-compose.yml`) to adjust server configuration

    web (odoo) -> the framework used

    db (postgres) -> the database used
    
    wdb (debuger) -> debug code

- open (`/config/odoo.conf`) to adjust odoo configuration

## Build on Docker cointainer

type (`docker-compose.yml`) command in the terminal

wait until all service started