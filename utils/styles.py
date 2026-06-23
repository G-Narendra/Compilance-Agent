"""
utils/styles.py
Separates bulky CSS from the main Streamlit application logic.
"""

import streamlit as st

def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* Global Font */
        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
        }

        /* Animated Gradient Header */
        .main-header {
            font-size: 3.5rem !important;
            font-weight: 800;
            background: linear-gradient(135deg, #A8C0FF 0%, #3f2b96 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            letter-spacing: -1px;
        }

        .sub-header {
            font-size: 1.15rem;
            color: #94A3B8;
            margin-bottom: 1.5rem;
            font-weight: 400;
            line-height: 1.6;
        }

        /* Use Case Banner */
        .use-case-banner {
            background: rgba(30, 41, 59, 0.6);
            border-left: 4px solid #6366F1;
            padding: 1.25rem 1.5rem;
            border-radius: 0.5rem;
            margin-bottom: 2.5rem;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            color: #E2E8F0;
            font-size: 0.95rem;
            line-height: 1.5;
        }

        .use-case-banner strong {
            color: #818CF8;
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.35rem 1rem;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 1rem;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        
        .status-active { 
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%);
            color: #C7D2FE; 
            border: 1px solid rgba(99, 102, 241, 0.3); 
        }

        /* Glassmorphism Cards */
        .metric-card {
            background: rgba(15, 23, 42, 0.6);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 1rem;
            padding: 1.5rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2), 0 4px 6px -2px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.1);
        }

        .metric-card h3 {
            color: #94A3B8;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 0;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }

        .metric-card p {
            color: #CBD5E1;
            font-size: 0.95rem;
            line-height: 1.5;
            margin: 0;
        }

        .finding-card {
            background: rgba(30, 41, 59, 0.4);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-left: 4px solid #6366F1;
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: all 0.2s ease;
        }

        .finding-card:hover {
            background: rgba(30, 41, 59, 0.6);
            border-color: rgba(255, 255, 255, 0.1);
        }

        /* Streamlit specific overrides */
        div.stButton > button {
            background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
            color: white;
            border: none;
            border-radius: 0.5rem;
            font-weight: 600;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.4);
        }
        
        div.stButton > button:hover {
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
            box-shadow: 0 6px 8px -1px rgba(99, 102, 241, 0.6);
            transform: translateY(-1px);
        }
    </style>
    """, unsafe_allow_html=True)
