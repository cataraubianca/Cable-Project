import React from "react";
import styles from "./case1.module.css"; 
import { VectorMap } from "react-jvectormap"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import announcements_after from "../data/announcements_after.json";
import announcements_before from "../data/announcements_before.json";
import flap_L1_destination from "../data/flap_L1_destination.json";
import flap_L1_source from "../data/flap_L1_source.json";
import flap_L2_destination from "../data/flap_L2_destination.json";
import flap_L2_source from "../data/flap_L2_source.json";
import real_withdrawal_L1_destination from "../data/real_withdrawal_L1_destination.json";
import real_withdrawal_L1_source from "../data/real_withdrawal_L1_source.json";
import real_withdrawal_L2_destination from "../data/real_withdrawal_L2_destination.json";
import real_withdrawal_L2_source from "../data/real_withdrawal_L2_source.json";
import anomalies from "../data/anomalies.json";
import { Navbar } from "../navbar/navbar";

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
const renderAnnouncementsTable = (data, title) => (
    <div>
        <h2>{title}</h2>
        <div className={styles.tableContainer}>
            <table className={styles.table}>
                <thead>
                    <tr>
                        <th className={styles.th}>Path</th>
                        <th className={styles.th}>Timestamp</th>
                    </tr>
                </thead>
                <tbody>
                    {data.map((item, index) => (
                        <tr key={index}>
                            <td className={styles.td}>{item[0].join(" -> ")}</td>
                            <td className={styles.td}>{new Date(item[1] * 1000).toLocaleString()}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    </div>
);

const renderAnomalies = (data, title) => (
    <div>
        <h2>{title}</h2>
        <div className={styles.tableContainer}>
            <table className={styles.table}>
                <thead>
                    <tr>
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

const renderHistogram = (data, title, before = true) => {
    const timestamps = data.map(item => new Date(item[1] * 1000));

    timestamps.forEach(timestamp => {
        const interval = Math.floor(timestamp.getMinutes() / 10) * 10; 
        console.log(`Timestamp: ${timestamp}, Interval: ${interval}`);
    });

    const intervalCounts = {};
    timestamps.forEach(timestamp => {
        const interval = Math.floor(timestamp.getMinutes() / 10) * 10; 
        const key = `${timestamp.getFullYear()}-${timestamp.getMonth() + 1}-${timestamp.getDate()} ${timestamp.getHours()}:${interval < 10 ? '0' : ''}${interval}`;
        if (!intervalCounts[key]) {
            intervalCounts[key] = 0;
        }
        intervalCounts[key]++;
    });

    const chartData = Object.keys(intervalCounts).map(key => ({
        interval: key,
        count: intervalCounts[key]
    }));

    return (
        <div>
            <h2>{title}</h2>
            <ResponsiveContainer width="100%" height={300}>
                <BarChart
                    data={chartData}
                    margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="interval" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="count" fill={before ? "#ff7300" : "#0088fe"} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};

export const Case1 = () => {
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
            <Navbar/>
            <h2>Map of countries with most delays from the country of interest</h2>
            <Map mapData={mapData} />
            {renderAnomalies(anomalies, "Anomalies")}
            <h2>Insights into the specific delay searched</h2>
            {renderHistogram(announcements_before, "Number of Announcements Before")}
            {renderAnnouncementsTable(announcements_before, "Announcements Before")}
            {renderHistogram(announcements_after, "Number of Announcements After", false)}
            {renderAnnouncementsTable(announcements_after, "Announcements After")}
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

