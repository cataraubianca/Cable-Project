import React from "react";
import styles from "./dw.module.css";
import { VectorMap } from "react-jvectormap";
import { Navbar } from "../navbar/navbar";
import flap_L1_destination from "C:/Users/Bianca/Desktop/France/first_year/second_semester/projet/flap_L1_destination_dw.json";
import flap_L1_source from "C:/Users/Bianca/Desktop/France/first_year/second_semester/projet/flap_L1_source_dw.json";
import flap_L2_destination from "C:/Users/Bianca/Desktop/France/first_year/second_semester/projet/flap_L2_destination_dw.json";
import flap_L2_source from "C:/Users/Bianca/Desktop/France/first_year/second_semester/projet/flap_L2_source_dw.json";
import real_withdrawal_L1_destination from "C:/Users/Bianca/Desktop/France/first_year/second_semester/projet/real_withdrawal_L1_destination_dw.json";
import real_withdrawal_L1_source from "C:/Users/Bianca/Desktop/France/first_year/second_semester/projet/real_withdrawal_L1_source_dw.json";
import real_withdrawal_L2_destination from "C:/Users/Bianca/Desktop/France/first_year/second_semester/projet/real_withdrawal_L2_destination_dw.json";
import real_withdrawal_L2_source from "C:/Users/Bianca/Desktop/France/first_year/second_semester/projet/real_withdrawal_L2_source_dw.json";
import anomalies from "C:/Users/Bianca/Desktop/France/first_year/second_semester/projet/anomalies_dw.json";

const Map = ({ mapData }) => {
    return (
        <div>
            <VectorMap
                map={"world_mill"}
                backgroundColor="transparent"
                zoomOnScroll={false}
                containerStyle={{
                    width: "100%",
                    height: "520px"
                }}
                containerClassName="map"
                regionStyle={{
                    initial: {
                        fill: "#e4e4e4",
                        "fill-opacity": 0.9,
                        stroke: "none",
                        "stroke-width": 0,
                        "stroke-opacity": 0
                    },
                    hover: {
                        "fill-opacity": 0.8,
                        cursor: "pointer"
                    },
                    selected: {
                        fill: "#2938bc"
                    },
                    selectedHover: {}
                }}
                regionsSelectable={true}
                series={{
                    regions: [
                        {
                            values: mapData,
                            scale: ["#ffff00", "#ff0000"], 
                            normalizeFunction: "polynomial"
                        }
                    ]
                }}
            />
        </div>
    );
};

const renderAnomalies = (data, title) => (
    <div>
        <h2>{title}</h2>
        <div className={styles.tableContainer}>
            <table className={styles.table}>
                <thead>
                    <tr>
                        <th className={styles.th}>ID</th>
                        <th className={styles.th}>Source</th>
                        <th className={styles.th}>Destination</th>
                        <th className={styles.th}>Avg</th>
                        <th className={styles.th}>M Avg</th>
                        <th className={styles.th}>Timestamp</th>
                        <th className={styles.th}>ASN</th>
                        <th className={styles.th}>Country</th>
                    </tr>
                </thead>
                <tbody>
                    {data.map((item, index) => (
                        <tr key={index}>
                            <td className={styles.td}>{index + 1}</td>
                            <td className={styles.td}>{item.anomaly_source}</td>
                            <td className={styles.td}>{item.anomaly_address}</td>
                            <td className={styles.td}>{item.anomaly_avg}</td>
                            <td className={styles.td}>{item.anomaly_mavg}</td>
                            <td className={styles.td}>{new Date(item.anomaly_timestamp * 1000).toLocaleString()}</td>
                            <td className={styles.td}>{item.asn}</td>
                            <td className={styles.td}>{item.country_code}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    </div>
);

const renderFlapL1SourceTable = (data, title) => (
    <div>
        <h2>{title}</h2>
        <div className={styles.tableContainer}>
            <table className={styles.table}>
                <thead>
                    <tr>
                        <th className={styles.th}>Source</th>
                        <th className={styles.th}>Destination</th>
                        <th className={styles.th}>Timestamp</th>
                        <th className={styles.th}>Count</th>
                    </tr>
                </thead>
                <tbody>
                    {data.map((item, index) => (
                        <tr key={index}>
                            <td className={styles.td}>{item[0]}</td>
                            <td className={styles.td}>{item[1]}</td>
                            <td className={styles.td}>{new Date(item[2] * 1000).toLocaleString()}</td>
                            <td className={styles.td}>{item[3]}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    </div>
);

export const Dw = () => {
    const countryCounts = anomalies.reduce((counts, anomaly) => {
        const countryCode = anomaly.country_code;
        counts[countryCode] = (counts[countryCode] || 0) + 1;
        return counts;
    }, {});

    const mapData = Object.keys(countryCounts).reduce((data, countryCode) => {
        data[countryCode] = countryCounts[countryCode];
        return data;
    }, {});

    return (
        <div>
            <Navbar />
            <h2>Map of countries with most delays from the country of interest</h2>
            <Map mapData={mapData} />
            {renderAnomalies(anomalies, "Anomalies")}
            <h2>Insights into the specific delay searched</h2>
            {renderFlapL1SourceTable(flap_L1_source, "Flaps Before Delay at Source")}
            {renderFlapL1SourceTable(real_withdrawal_L1_source, "Withdrawals Before Delay at Source")}
            {renderFlapL1SourceTable(flap_L2_source, "Flaps After Delay at Source")}
            {renderFlapL1SourceTable(real_withdrawal_L2_source, "Withdrawals After Delay at Source")}
            {renderFlapL1SourceTable(flap_L1_destination, "Flaps Before Delay at Destination")}
            {renderFlapL1SourceTable(real_withdrawal_L1_destination, "Withdrawals Before Delay at Destination")}
            {renderFlapL1SourceTable(flap_L2_destination, "Flaps After Delay at Destination")}
            {renderFlapL1SourceTable(real_withdrawal_L2_destination, "Withdrawals After Delay at Destination")}
        </div>
    );
};
