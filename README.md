HackTheCrisis3
================

Hacking the COVID-19 crisis one candy at a time
------------
Introduction
------------
This repo was created during Hack the Crisis Sweden hackathon on 4th - 5th of April, 2020.
It a minimal implementation for www.cleanhandscandy.org


Problem:
------------
Many people were not used to washing their hands often and thoroughly before the crisis.
Obtaining such habit is no easy task, especially for workers who have to deliver non-stop even during quarantine, such as grocery  shop associates who stock shelves or assemble carts for home delivery.


Solution:
------------
We want to reward employees for washing their hands often and thoroughly and get that habit to stick by rewards.
Candy is a good reward

Solution flow:
------------
- employee touch their NFC tag to receiver right before they wash their hands
- receiver reads tag and sends POST to backend server
- backend server logs and, thourgh websockets, updates any subscribed browser displayed info
- increment of reward pops up near employees' eyes
- employee craves more candy, hence washes their hands more often

![alt text](https://raw.githubusercontent.com/rEphEOn/HackTheCrisis3/master/IMG_20200405_205039.jpg)
