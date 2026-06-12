import { useEffect, useState } from "react";
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer
} from "recharts";
import { getDashboard , getStatistics} from "../api/admin";

export default function Admin() {
    console.log("ADMIN PAGE CHARGEE");
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState([]);

    const loadStatistics = async (days) => {

    try {

        const response = await getStatistics(days);

        setStats(response.data);

    } catch (error) {

        console.error(error);

    }
};
    useEffect(() => {

        const loadData = async () => {

            try {
                console.log("AVANT APPEL API");

                const res = await getDashboard();
                console.log("REPONSE API :", res.data);


                setData(res.data);
                {/*const stats = await getStatistics(30);*/}
                await loadStatistics(30);
                 console.log("STATISTIQUES :", stats.data);
                 {/*setStats(stats.data);*/}

            } catch (err) {

                console.error("ERREUR API :",err);

            } finally {

                setLoading(false);

            }
        };

        loadData();

    }, []);

    if (loading)
        return <div>Chargement...</div>;
    {/*console.log(res.data.etudiants_free);*/}
    {/*const loadData = async () => {

    try {
        console.log("AVANT APPEL API");

        const res = await getDashboard();

           console.log(res.data.etudiants_free);
        console.log("REPONSE API : ", res.data);


           setData(res.data.etudiants_free);
        setData(res.data);

    } catch (err) {

        console.error("ERROR API",err);

    } finally {

        setLoading(false);

    }
    };*/}
    {/*const chartData = stats.summaries || [];*/}
    const chartData = stats;
    console.log("STATS =", stats);
    console.log("CHART DATA =", chartData);
    return (

        <div style={{
            maxWidth: "1200px",
            margin: "0 auto",
            padding: "2rem"
        }}>

            <h1>Administration</h1>

            <hr />
              <h2>Évolution des activités IA</h2>
              <div style={{ marginBottom: "20px" }}>

    <button onClick={() => loadStatistics(7)}>
        7 jours
    </button>

    <button onClick={() => loadStatistics(30)}>
        30 jours
    </button>

    <button onClick={() => loadStatistics(90)}>
        90 jours
    </button>

    <button onClick={() => loadStatistics(365)}>
        1 an
    </button>

</div>

<div style={{ width: "100%", height: 400 }}>

    <ResponsiveContainer width="100%" height="100%">

        <LineChart data={chartData}>

            <CartesianGrid strokeDasharray="3 3" />

            <XAxis dataKey="day" />

            <YAxis />

            <Tooltip />

            <Legend />

            <Line
    type="monotone"
    dataKey="summaries"
    name="Résumés"
    stroke="#ff9900"
    strokeWidth={3}
    dot={{ r: 5 }}
/>

<Line
    type="monotone"
    dataKey="flashcards"
    name="Flashcards"
    stroke="#00aa00"
    strokeWidth={3}
    dot={{ r: 5 }}
/>

<Line
    type="monotone"
    dataKey="quizzes"
    name="Quiz"
    stroke="#0066ff"
    strokeWidth={3}
    dot={{ r: 5 }}
/>

<Line
    type="monotone"
    dataKey="total"
    name="Total"
    stroke="#ff0000"
    strokeWidth={3}
    dot={{ r: 5 }}
/>

        </LineChart>

    </ResponsiveContainer>

</div>
            <h2>Étudiants Free</h2>

            <table border="1" cellPadding="10">

                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Résumés IA</th>
                        <th>Flashcards IA</th>
                        <th>Quiz réalisés</th>
                    </tr>
                </thead>

                <tbody>

                    {data.etudiants_free.map(student => (

                        <tr key={student.id}>

                            <td>{student.username}</td>

                            <td>{student.email}</td>
                     {/*
                            <td>{student.summaries}</td>

                            <td>{student.flashcards}</td>

                            <td>{student.quizzes}</td>
*/}
                            <td>{student.summaries_count}</td>

                            <td>{student.flashcards_count}</td>

                            <td>{student.quiz_attempts_count}</td>
                        </tr>

                    ))}

                </tbody>

            </table>

            <br />

            <h2>Étudiants Premium</h2>

            <table border="1" cellPadding="10">

                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Superviseur</th>
                        <th>Résumés IA</th>
                        <th>Flashcards IA</th>
                        <th>Quiz réalisés</th>
                    </tr>
                </thead>

                <tbody>

                    {data.etudiants_premium.map(student => (

                        <tr key={student.id}>

                            <td>{student.username}</td>

                            <td>{student.email}</td>

                            <td>{student.superviseur || "-"}</td>
{/*
                            <td>{student.summaries}</td>

                            <td>{student.flashcards}</td>

                            <td>{student.quizzes}</td>*/}

                            <td>{student.summaries_count}</td>

                            <td>{student.flashcards_count}</td>

                            <td>{student.quiz_attempts_count}</td>

                        </tr>

                    ))}

                </tbody>

            </table>

            <br />

            <h2>Superviseurs</h2>

            <table border="1" cellPadding="10">

                <thead>

                    <tr>

                        <th>Nom</th>

                        <th>Email</th>

                        <th>Étudiants supervisés</th>

                    </tr>

                </thead>

                <tbody>

                    {data.superviseurs.map(superviseur => (

                        <tr key={superviseur.id}>

                            <td>{superviseur.username}</td>

                            <td>{superviseur.email}</td>

                            <td>

                                {superviseur.etudiants.length > 0
                                    ? superviseur.etudiants.join(", ")
                                    : "Aucun"}

                            </td>

                        </tr>

                    ))}

                </tbody>

            </table>

        </div>
    );
}