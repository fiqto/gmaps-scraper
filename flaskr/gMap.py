from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_file
)
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import pandas as pd
import os
import io
from flaskr.db import get_db

bp = Blueprint('gMap', __name__)

@bp.route('/')
def index():
    db = get_db()
    items = db.execute(
        'SELECT id, name, rate, category, address, created'
        ' FROM item'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('index.html', items=items)

@bp.route('/export')
def export(path="flaskr", file_name="data.csv"):
    db = get_db()
    items = db.execute(
        'SELECT id, name, rate, category, address, created'
        ' FROM item'
        ' ORDER BY created DESC'
    ).fetchall()

    df = pd.DataFrame(items)
    os.makedirs(path, exist_ok=True)
    df.to_csv(os.path.join(path, file_name), index=False)

    return send_file(file_name, as_attachment=True)


@bp.route('/create', methods=['POST'])
def create():
    url = 'https://www.google.com/maps'
    search = request.form['search']
    total_str = request.form['total']
    total = int(total_str)
    max_count = total

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        page = browser.new_page()
        page.set_viewport_size(
            {'width': 500, 'height': 1000}
        )
        page.goto(url)
        page.get_by_label('Telusuri Google Maps').fill(search)
        page.keyboard.press('Enter')
        time.sleep(3)
        page.wait_for_load_state('networkidle')

        # Check the amount of data
        count = 0
        while count < max_count:
            page.keyboard.press('End')
            time.sleep(2)

            html = page.inner_html('div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde.ecceSd')
            soup = BeautifulSoup(html, 'html.parser')
            items = []
            count = 0
            for item in soup.find_all('div',{'class': 'Nv2PK THOPZb CpccDe'}):
                name = item.find('a', {'class': 'hfpxzc'}).get('aria-label')
                items.append({
                    'name': name
                })
                count += 1
                if count == max_count:
                    break

        for detail in items:
            name = detail['name']
            found_name = False
            while not found_name:
                page.keyboard.press('End')
                time.sleep(2)
                try:
                    page.get_by_label(name).click()
                    found_name = True
                    break
                except Exception:
                    pass

            time.sleep(3)
            html = page.inner_html('div.w6VYqd')
            soup = BeautifulSoup(html, 'html.parser')
            name = soup.find('h1', {'class': 'DUwDvf lfPIob'}).text
            rate = soup.find('div', {'class': 'F7nice'}).text
            category = soup.find('button', {'class': 'DkEaL'}).text
            address = soup.find('div', {'class': 'Io6YTe fontBodyMedium kR99db'}).text

            db = get_db()
            db.execute(
                'INSERT INTO item (name, rate, category, address)'
                ' VALUES (?, ?, ?, ?)',
                (name, rate, category, address)
            )
            db.commit()

            page.get_by_label('Kembali', exact=True).click()
            time.sleep(3)

    return redirect(url_for('gMap.index'))

@bp.route('/delete')
def delete():
    db = get_db()
    db.execute('DELETE FROM item')
    db.commit()
    return redirect(url_for('gMap.index'))