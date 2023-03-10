import streamlit as st
from datetime import datetime,date,timedelta
import pandas as pd
import requests



def fetch(session, url):
    try:
        result = session.get(url)
        return result.json()
    except Exception as e:
        print(e)
        return {}

# st.cache
def fetch_analytics(type,session, start_date, end_date):
    data = fetch(session,f"""http://localhost:8000/analytics/{type}/?start={start_date}&end={end_date}""")
    return data

def main():
    ## set page config for streamlit app
    st.set_page_config(page_title="Pocketed Metrics Dashboard",layout='wide', initial_sidebar_state='expanded')
    session = requests.Session()
    ## import css styling
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


    today = datetime.today()
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)
    
    sidebar = st.sidebar
    sidebar.header('Pocketed Analytics')
    sidebar.markdown('''
    ---
    # Quarterly Goals
    ''')
    sidebar.markdown("Objective 1: $65K B2C SaaS Revenue")
    sidebar.markdown("Objective 2: $40K B2C Service Revenue")
    sidebar.markdown("Objective 3: $15K B2B SaaS Revenue")
    sidebar.markdown("")
    sidebar.markdown("")
    sidebar_button = sidebar.button("Refresh")
    if sidebar_button:
        st.experimental_rerun()
        

    since, total = st.tabs(["Date Range","Total"])
    
    with since:

        start_date = st.date_input('Start date:', last_week) 
        end_date = st.date_input('End date:', yesterday, key='2') 
        # add a day so that it's inclusive of input date
        end_date = end_date + timedelta(days=1)
        
        display_user_metrics(session, start_date, end_date)
        with st.spinner("Generating Free Trial Metrics..."):
            display_freetrial_metrics(session, start_date, end_date)
        with st.spinner("Generating General Saas Metrics..."):
            display_saas_metrics(session, start_date, end_date)
        with st.spinner("Generating Revenue Metrics..."):
            display_revenue_metrics(session, start_date, end_date)


    with total:
        start_of_pocketed = date(2020,1,1)
        end_date = st.date_input('End date:', yesterday, key='1') 
        # add a day so that it's inclusive of input date
        end_date = end_date + timedelta(days=1)
        st.cache()
        display_user_metrics(session, start_of_pocketed, end_date)
        with st.spinner("Generating Free Trial Metrics..."):
            st.cache()
            display_freetrial_metrics(session, start_of_pocketed, end_date)
        with st.spinner("Generating General Saas Metrics..."):
            st.cache()
            display_saas_metrics(session, start_of_pocketed, end_date)
        with st.spinner("Generating Revenue Metrics..."):
            display_revenue_metrics(session, start_of_pocketed, end_date)

    
    


def display_user_metrics(session, start_date, end_date):

    data = fetch_analytics("user", session, start_date, end_date)
    users = data.get('users')
    referral_users = data.get('referrals')

    st.markdown('### User Metrics')
    col0, col1,  = st.columns(2)
    
    col0.metric("Users", users, help="Users created within time period")
    col1.metric("Users with referral code", referral_users, help="Users created **with referral code** within time period")

def display_freetrial_metrics(session, start_date, end_date):

    data = fetch_analytics("freetrial", session, start_date, end_date)
    free_trial_starts = data.get('free_trials')
    free_trial_cancellations = data.get('free_trial_cancellations')
    free_trial_conversions = data.get('free_trial_conversions')

    st.markdown('### Free Trial Metrics')
    col2, col3, col4 = st.columns(3)
    col2.metric("Free Trial Starts", free_trial_starts, help="Users who **started a trial** within time period")
    col3.metric("Free Trial Cancellations", free_trial_cancellations, help="Trialing users who cancelled and ended their trial, or cancelled Auto-Renewal within time period")
    col4.metric("Free Trial Conversions", free_trial_conversions, help="Users who converted from **'trialing'** to **'active'** within time period")
    
def display_saas_metrics(session, start_date, end_date):

    data = fetch_analytics("saas", session, start_date, end_date)
    basic_subscriptions = data.get("basic_subscriptions")
    basic_subs_non_trial = data.get("basic_subs_non_trial")
    basic_subs_trial = data.get("basic_subs_trial")
    pplus_subscriptions = data.get('pplus_subscriptions')
    concierge_subscriptions = data.get('concierge_subscriptions')
    total_active_subscriptions = data.get('total_active_subscriptions')
    new_user_conversion = data.get("new_user_conversion")
    churn = data.get("churn")
    cancellations = data.get("cancellations")
    

    st.markdown('### General Saas Metrics')
    col5a, col5b, col5c, col5d = st.columns(4)
    col5a.metric("Total Active Subscriptions", total_active_subscriptions, help="Basic subscriptions + Plus subscriptions + Concierge Subscriptions")
    col5b.metric("New User Conversion", f"{new_user_conversion}%", help="Total Active Subscriptions / Users")
    col5c.metric("Churn", f"{churn}%", help="Non-trial Cancellations / Total Active Subscriptions")
    col5d.metric("Cancellations", f"{cancellations}", help="Non-trial cancellations (cancelled OR set to cancel)")
    st.markdown('### Active Subscriptions')
    col5, col6, col7 = st.columns(3)
    col5.metric("Basic Subscriptions", basic_subscriptions, help=f"New Basic Subscriptions, made up of {basic_subs_trial} trial conversions, and {basic_subs_non_trial} non-trial conversions")
    col6.metric("Pocketed+ Subscriptions", pplus_subscriptions)
    col7.metric("Concierge Subscriptions", concierge_subscriptions)

def display_revenue_metrics(session, start_date, end_date):
    data = fetch_analytics("revenue", session, start_date, end_date)
    saas_cad = data.get("saas")
    service_cad = data.get("service")
    refunds_cad = data.get("refunds")
    refunds_count = data.get("refunds_count")
    total_cad = data.get("total")
    
    st.markdown("""
    ### Analytics
    All dollar amounts are in CAD and are before tax and after fees.
     """)
    col8, col9 = st.columns(2)
    col8.metric("SaaS Revenue", f"${saas_cad}")
    col9.metric("Service Revenue", f"${service_cad}")

    col10,col11 = st.columns(2)
    col10.metric("Refunds", f"${refunds_cad}CAD", help=f"{refunds_count} refunds this period")
    col11.metric("Total Net Revenue", f"${total_cad}", help=f"Saas revenue + Service revenue - Refunds")

def get_current_quarter():
    # Get the current date
    now = datetime.now()

    # Get the current quarter
    current_quarter = (now.month - 1) // 3 + 1

    # Get the start date of the current quarter
    quarter_start = datetime(now.year, 3 * current_quarter - 2, 1)

    # Get the end date of the current quarter
    quarter_end = quarter_start + timedelta(days=90)

    return{
        "qs" : quarter_start,
        "qe" : quarter_end

    }

if __name__ == '__main__':
    main()
