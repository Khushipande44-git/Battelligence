# 🔋 Battelligence – Smart Battery Management Dashboard

Battelligence is a real-time, interactive, and customizable **Battery Management System (BMS)** dashboard built with **Streamlit** and **Plotly**. It allows users to monitor, analyze, and control multiple battery cells with support for various chemistries like LFP, NMC, LTO, and LCO.

---

## 🚀 Features

- 📊 Live dashboard with system metrics (voltage, current, temperature, capacity).
- ⚙️ Configurable battery setup (cell type, voltage, current).
- 📈 Real-time data visualization (charts & alerts).
- 🎛️ Interactive control panel with emergency stop.
- 📋 Analytical tools (efficiency, power density, radar charts).
- 💾 Export reports in JSON and CSV formats.

---

## 🧰 Tech Stack

- Python 3.7+
- [Streamlit](https://streamlit.io/)
- [Plotly](https://plotly.com/)
- [Pandas](https://pandas.pydata.org/)
- [NumPy](https://numpy.org/)

---

## ⚙️ How to Run the Project

1. **Clone the Repository**
'''bash
git clone https://github.com/yourusername/voltura-dashboard.git
cd voltura-dashboard

2. **Create Virtual Environment**
'''bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

3.**Install Dependencies**
'''bash
pip install -r requirements.txt

4.**Run the Streamlit App**
'''bash
streamlit run battery_dashboard.py

5. **📁 File Structure**
'''bash
voltura-dashboard/
├── battery_dashboard.py     # Main Streamlit application
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation

6.**📥 Future Enhancements**
Integration with live sensor data (IoT).
User authentication and role-based access.
Cloud-based data logging and notifications.

7.**👩‍💻 Author**
Khushi Pande
📧 khushipande44@gmail.com

8.**📄 License**
This project is open-source and available under the MIT License.

---

