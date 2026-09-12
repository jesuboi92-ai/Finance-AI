import base64
import io
import sys
import pandas as pd
import pypdf
from PIL import Image
import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="Talous-AI & Vaurastumisassistentti", page_icon="📈", layout="centered"
)

# --- TURVALLISUUS: HAETAAN API-AVAIN PALVELIMELTA TAI SIVUPALKIN KENTÄSTÄ ---
try:
    default_api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    default_api_key = ""

st.title("📈 Talous-AI & Vaurastumisassistentti (Free & Pro)")
st.write(
    "Alykas talousassistentti arkeen ja sijoittamiseen. "
    "Kayta ilmaisia perustoimintoja tai paivita Pro-versioon!"
)

# --- SIVUPALKKI: TILAUS & PRO-AKTIVOINTI ---
st.sidebar.header("💎 Kayttooikeus & Tilaukset")

if "is_pro" not in st.session_state:
    st.session_state.is_pro = False

with st.sidebar.expander("🔑 OpenAI API-asetukset", expanded=not default_api_key):
    st.markdown("Syota OpenAI:n API-avain tekoalytoimintoja varten.")
    user_api_input = st.text_input("OpenAI API-avain", value="", type="password", key="user_openai_key")
    if user_api_input:
        api_key = user_api_input.strip()
    else:
        api_key = default_api_key.strip()

st.sidebar.markdown("---")

if st.session_state.is_pro:
    st.sidebar.success("✅ Pro-tila aktivoituna tassa istunnossa!")
    if st.sidebar.button("Kirjaudu ulos Pro-tilasta"):
        st.session_state.is_pro = False
        st.rerun()
else:
    st.sidebar.info("Olet **Ilmaisversiossa**.")
    st.sidebar.markdown("---")
    st.sidebar.subheader("🚀 Paivita Pro-versioon")
    st.sidebar.markdown(
        "Hanki kaikki tekoalyominaisuudet, PDF-palkkalaskelman luku, kuvaskanneri ja alykas hintavertailu!"
    )
    st.sidebar.markdown("**Hinnat:**")
    st.sidebar.markdown("- 🌟 **4,90 € / kk**")
    st.sidebar.markdown("- 🔥 **49,00 € / vuosi** *(saasta 17%)*")
    
    with st.sidebar.expander("🔑 Minulla on jo aktivointikoodi", expanded=True):
        entered_code = st.text_input("Syota lisenssikoodi / PIN", value="", type="password", key="entered_pin")
        if st.button("Aktivoi Pro"):
            if entered_code.strip() == "salasana123": 
                st.session_state.is_pro = True
                st.success("Pro aktivoitu onnistuneesti!")
                st.rerun()
            else:
                st.error("Virheellinen koodi. Kokeile salasana123")

    st.sidebar.markdown("---")
    st.sidebar.markdown("💡 *Haluatko ostaa Pro-oikeuden? Ota yhteys yllapitajaan.*")

is_pro_unlocked = st.session_state.is_pro

# Paasovelluksen valilehdet
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📝 Tulot & Menot", 
        "🎯 Sijoituspuskuri", 
        "💡 Smart Budget", 
        "🏷️ Omat Hinnat",
        "🛒 Perusruokabudjetti",
        "🍳 Pro: Ruokalista & Hintavertailu"
    ]
)

if "custom_products" not in st.session_state:
    st.session_state.custom_products = pd.DataFrame(
        [
            {"Poista": False, "Tuote / Pakkaus": "Kanafilee (400g)", "Kauppa": "Prisma", "Hinta (€)": 4.50},
            {"Poista": False, "Tuote / Pakkaus": "Maito (1l)", "Kauppa": "S-Market", "Hinta (€)": 1.19},
            {"Poista": False, "Tuote / Pakkaus": "Raejuusto (400g)", "Kauppa": "Prisma", "Hinta (€)": 2.15},
            {"Poista": False, "Tuote / Pakkaus": "Banaanit (niput)", "Kauppa": "Lidl", "Hinta (€)": 2.50},
            {"Poista": False, "Tuote / Pakkaus": "Riisi (1kg)", "Kauppa": "K-Citymarket", "Hinta (€)": 1.60},
        ]
    )

# --- TAB 1: TULOT & MENOT ---
with tab1:
    st.subheader("1. Tulot & Manuaaliset menot")
    
    if is_pro_unlocked:
        st.markdown("### 📄 [PRO] Tuo tulotiedot suoraan PDF-palkkalaskelmasta")
        uploaded_pdf = st.file_uploader("Lataa palkkalaskelma (PDF)", type=["pdf"], key="pdf_uploader_main")
        
        if uploaded_pdf is not None:
            if not api_key:
                st.error("⚠️ Syota OpenAI API-avain sivupalkin asetuksiin ennen tiedoston lukemista.")
            else:
                try:
                    reader = pypdf.PdfReader(uploaded_pdf)
                    pdf_text = ""
                    for page in reader.pages:
                        pdf_text += page.extract_text() or ""
                    
                    with st.spinner("Tekoaly lukee palkkatietoja PDF:sta..."):
                        client = OpenAI(api_key=api_key)
                        prompt = (
                            "Etsi seuraavasta palkkalaskelman tekstista NETTO-palkka (kateen jaava summa) "
                            "seka BRUTTO-palkka. Palauta tulos muodossa: Netto: [numero], Brutto: [numero].\n\n"
                            f"Teksti:\n{pdf_text[:3000]}"
                        )
                        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
                        st.info(f"AI:n loytamat tiedot tekstista: {resp.choices[0].message.content}")
                except Exception as e:
                    st.error("Virhe tiedoston kasittelyssa.")
    else:
        st.info("🔒 **PDF-palkkalaskelman automaattinen luku** vaatii Pro-version (4,90 €/kk).")

    col1, col2 = st.columns(2)
    with col1:
        monthly_income = st.number_input("Netto-kuukausitulot (€)", min_value=0.0, value=2500.0, step=50.0)
        vuokra = st.number_input("Vuokra / Asuntolaina (€)", min_value=0.0, value=800.0, step=50.0)
        sahko = st.number_input("Sahko (€)", min_value=0.0, value=40.0, step=10.0)
        vesi = st.number_input("Vesi (€)", min_value=0.0, value=20.0, step=5.0)
    with col2:
        ruokakulut = st.number_input("Arvioidut ruokakulut (kauppa) (€)", min_value=0.0, value=350.0, step=25.0)
        suoratoisto = st.number_input("Suoratoistopalvelut (€)", min_value=0.0, value=45.0, step=5.0)
        muut_menot = st.number_input("Muut pakolliset kulut (€)", min_value=0.0, value=150.0, step=25.0)

    total_expenses = vuokra + sahko + vesi + ruokakulut + suoratoisto + muut_menot
    net_left = monthly_income - total_expenses
    st.info(f"📊 Yhteenveto: Tulot {monthly_income} € | Menot **{total_expenses} €** | Jaljelle jaa: **{net_left} €**")

# --- TAB 2: SIJOITUSPUSKURI ---
with tab2:
    st.subheader("2. Sijoittamiskeskeinen optimointi & Korkoa korolle -laskuri")
    current_balance = st.number_input("Tililla oleva nykyinen kayttoraha yhteensa (€)", value=3500.0, key="curr_bal")
    buffer_need = st.number_input("Turvapuskurin tavoite (€)", value=2000.0, key="buff_need")

    if st.button("Laske sijoitettava ylijaama"):
        excess_cash = current_balance - buffer_need
        if excess_cash > 0:
            st.success(f"💡 **Sijoituspotentiaali:** Noin **{excess_cash:.0f} euroa** puskurin ylittavaa rahaa.")
        else:
            st.info("Keskity ensin saavuttamaan turvapuskuritavoite.")

    st.markdown("---")
    col_inv1, col_inv2 = st.columns(2)
    with col_inv1:
        alkup_sijoitus = st.number_input("Alkusijoitus (€)", value=1000.0, step=100.0)
        kk_sijoitus = st.number_input("Kuukausisaasto (€)", value=150.0, step=25.0)
    with col_inv2:
        sijoitus_aika_vuotta = st.slider("Sijoitusaika (vuotta)", 1, 40, 10)
        arvioitu_tuotto_prosentti = st.slider("Arvioitu vuosituotto (%)", 0.0, 20.0, 7.0, 0.5)

    kokonaissumma = alkup_sijoitus
    kuukausi_tuotto = arvioitu_tuotto_prosentti / 100 / 12
    for _ in range(sijoitus_aika_vuotta * 12):
        kokonaissumma = (kokonaissumma + kk_sijoitus) * (1 + kuukausi_tuotto)
    
    st.info(f"📊 **Salkun arvo {sijoitus_aika_vuotta} v. jalkeen:** **{kokonaissumma:,.0f} €**")

    if is_pro_unlocked:
        st.markdown("### 🤖 [PRO] Kriittinen tekoalyanalyysi sijoitussuunnitelmasta")
        sijoitus_kohde_kuvaus = st.text_area("Strategia:", "Sijoitan globaaliin indeksirahastoon.")
        if st.button("Pyyda Pro AI-analyysi"):
            if api_key:
                client = OpenAI(api_key=api_key)
                resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": f"Analysoi kriittisesti sijoitusstrategiaa: {sijoitus_kohde_kuvaus}"}])
                st.markdown(resp.choices[0].message.content)
            else:
                st.error("⚠️ Syota OpenAI API-avain sivupalkin asetuksiin.")
    else:
        st.markdown("*(🔒 Pro-kayttajat saavat tahan tekoalyn tarkan riskianalyysin).*")

# --- TAB 3: SMART BUDGET ---
with tab3:
    st.subheader("3. Smart Budget & Viikkoseuranta")
    weekly_food_target = st.number_input("Viikoittainen ruokabudjetti (€)", value=80.0)
    actual_food_spent = st.number_input("Talla viikolla kaytetty (€)", value=65.0)
    
    if is_pro_unlocked:
        if st.button("Hae Pro-palaute viikon kulutuksesta"):
            if api_key:
                client = OpenAI(api_key=api_key)
                resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": f"Arvioi viikkobudjettia (tavoite {weekly_food_target}, toteutunut {actual_food_spent}) huumorilla."}])
                st.markdown(resp.choices[0].message.content)
            else:
                st.error("⚠️ Syota OpenAI API-avain sivupalkin asetuksiin.")
    else:
        st.info("🔒 AI-palaute budjetille vaatii Pro-tilan.")

# --- TAB 4: HINNAT & KUITTISKANNERI ---
with tab4:
    st.subheader("🏷️ Omat tuotehinnat & Kuvaskanneri")
    
    if is_pro_unlocked:
        st.markdown("### 📸 [PRO] Alykas Kuvaskanneri")
        uploaded_files = st.file_uploader("Lataa kuitteja", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        if uploaded_files:
            st.success(f"Ladattu {len(uploaded_files)} kuvaa skannattavaksi.")
    else:
        st.info("🔒 Kuittien automaattinen tekoalyskanneri on Pro-ominaisuus.")

    st.markdown("### 📋 Omat tallennetut hinnat")
    edited_df = st.data_editor(st.session_state.custom_products, num_rows="dynamic", key="product_editor")
    if "Poista" in edited_df.columns:
        st.session_state.custom_products = edited_df[edited_df["Poista"] == False].reset_index(drop=True)

# --- TAB 5: PERUSRUOKABUDJETOIJA ---
with tab5:
    st.subheader("🛒 Arjen Perusruokabudjetti & Alykkaat Saastovinkit")
    st.write("Tarkista suositellut ruokabudjetit ja nappaa parhaat arjen saastokikat kayttöösi!")

    family_size_basic = st.selectbox("Valitse talouden koko", ["1 henkilo", "2 henkiloa", "Perhe (3-4 hlö)"], key="t5_family")
    
    if family_size_basic == "1 henkilo":
        suf_suositus = "200 – 260 € / kk (~50–65 € / vko)"
        kerta_ostos = "Noin 40–50 € / kauppareissu"
    elif family_size_basic == "2 henkiloa":
        suf_suositus = "350 – 450 € / kk (~90–110 € / vko)"
        kerta_ostos = "Noin 70–90 € / kauppareissu"
    else:
        suf_suositus = "600 – 800 € / kk (~150–200 € / vko)"
        kerta_ostos = "Noin 120–160 € / kauppareissu"

    st.info(f"📊 **Suositeltu ruokabudjetti:** {suf_suositus} | Suositeltava kertaostos: {kerta_ostos}")

    st.markdown("---")
    st.markdown("### 💡 Parhaat ilmaiset saastovinkit ruokakauppaan")
    
    col_vinkki1, col_vinkki2 = st.columns(2)
    with col_vinkki1:
        st.markdown("#### 1. Suunnitelmallisuus & Kauppalista")
        st.write(
            "- **Kay kaupassa vain kerran tai kahdesti viikossa:** "
            "Jatkuva herateostoksilla kaynti kasvattaa ruokamenoja.\n"
            "- **Ala koskaan mene kauppaan nalkaisena:** "
            "Nalkaisena ostoskoriin tarttuu helposti kalliita tuotteita."
        )
        st.markdown("#### 2. Tuotemerkit & Hinnoittelu")
        st.write(
            "- **Suosi kauppojen omia merkkeja** (esim. Rainbow, K-Menu, Pirkka): "
            "Tuotteet ovat usein samaa laatua.\n"
            "- **Tarkista kilohinta:** Ala tuijota pelkkaa pakkaushintaa."
        )
    with col_vinkki2:
        st.markdown("#### 3. Havikkiruoka & Sesongit")
        st.write(
            "- **Hyödynnä laputetut tuotteet:** "
            "Etsi -30% ja -60% punalappuiset tuotteet.\n"
            "- **Syo sesongin mukaan:** "
            "Juurekset ja kaalit ovat edullisimmillaan."
        )
        st.markdown("#### 4. Ruoanlaitto & Pakastaminen")
        st.write(
            "- **Tee kerralla isompi satsi:** "
            "Padat ja laatikkoruoat riittavat useammalle aterialle.\n"
            "- **Hyödynnä pakastinta:** "
            "Jaa ylijäämäruoka annosrasioihin."
        )

# --- TAB 6: PRO - RUOKALISTA & HINTAVERTAILU ---
with tab6:
    st.subheader("🍳 [PRO] Tarkka ruokalista & Kauppojen vierekkäinen hintavertailu")
    
    if is_pro_unlocked:
        col_a, col_b = st.columns(2)
        with col_a:
            diet_choice = st.selectbox("Valitse ruokavalio", ["Sekasyöjä", "Kasvissyöjä", "Vegaani", "Gluteeniton", "Laktoositon"], key="t6_diet")
            daily_calories = st.number_input("Tarkka kaloritavoite (kcal)", min_value=1200, max_value=5000, value=2000, step=50, key="t6_cal")
            days_count = st.slider("Ajanjakso (päivää)", min_value=1, max_value=7, value=7, key="t6_days")
        with col_b:
            goal_choice = st.selectbox(
                "Tavoite", 
                [
                    "Terveellinen perusruokavalio",
                    "📉 Laihdutus / Painonhallinta (Kalorivaje)", 
                    "💪 Lean Bulk (Lihasmassan kasvu)",
                    "🔥 Lean Cut (Kiristely)",
                    "🏷️ Tarjousten hyödyntäminen / Halvin"
                ],
                key="t6_goal"
            )
            meals_per_day = st.slider("Aterioita / päivä", min_value=1, max_value=6, value=3, key="t6_meals")

        family_size_pro = st.selectbox("Talouden koko (kenelle ruuat mitoitetaan)", ["1 henkilö", "2 henkilöä", "Perhe (3-4 hlö)", "Suurperhe (5+ hlö)"], key="t6_family")

        allergies_input = st.text_input("Allergiat / Vältettävät aineet", value="", key="t6_allergies")
        stores_to_compare = st.multiselect("Valitse kaupat vertailuun", ["Lidl", "S-Market", "Prisma", "K-Market", "K-Citymarket"], default=["Lidl", "Prisma", "S-Market"], key="t6_stores")

        if st.button("Generoi Pro-ruokalista ja hintavertailutaulukko"):
            if not api_key:
                st.error("⚠️ Syötä OpenAI API-avain sivupalkin 'OpenAI API-asetukset' -laatikkoon ennen tekoälypyynnön tekemistä.")
            elif len(stores_to_compare) < 1:
                st.warning("Valitse vähintään yksi kauppa.")
            else:
                client = OpenAI(api_key=api_key)
                stores_str = ", ".join(stores_to_compare)
                prompt = (
                    f"Suunnittele {days_count} päivän ruokalista taloudelle, jonka koko on '{family_size_pro}': "
                    f"ruokavalio {diet_choice}, kaloritavoite per henkilö {daily_calories} kcal/pvä, "
                    f"tavoite {goal_choice}, aterioita {meals_per_day} kpl/pvä, allergiat: '{allergies_input}'.\n"
                    f"Let's write in Finnish. Luo tarkka ostoslista koko taloudelle oikeilla pakkaus- ja määräyksiköillä (esim. grammoina tai paketteina) "
                    f"sekä Markdown-taulukko, jossa on sarakkeina [Tuote, Tarvittava määrä, {stores_str}]. "
                    f"Laske taulukon loppuun YHTEENSÄ (€) -summat jokaiselle kaupalle."
                )
                with st.spinner("Luodaan Pro-ruokalistaa ja hintavertailua..."):
                    try:
                        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
                        st.markdown(resp.choices[0].message.content)
                    except Exception as e:
                        st.error("Virhe tekoälypyynnössä.")
    else:
        st.warning("🔒 **Tämä välilehti on lukittu Pro-käyttäjille (4,90 €/kk).** Päivitä Pro-versioon sivupalkin kautta avataksesi edistyneen ruokalistageneraattorin ja hintavertailun!")
