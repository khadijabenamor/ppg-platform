import { useEffect, useState } from "react";
import { getDashboard } from "../api/admin";

export default function Admin() {

    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {

        const loadData = async () => {

            try {

                const res = await getDashboard();

                setData(res.data);

            } catch (err) {

                console.error(err);

            } finally {

                setLoading(false);

            }
        };

        loadData();

    }, []);

    if (loading)
        return <div>Chargement...</div>;

    return (

        <div style={{
            maxWidth: "1200px",
            margin: "0 auto",
            padding: "2rem"
        }}>

            <h1>Administration</h1>

            <hr />

            <h2>Étudiants Free</h2>

            <table border="1" cellPadding="10">

                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Email</th>
                    </tr>
                </thead>

                <tbody>

                    {data.etudiants_free.map(student => (

                        <tr key={student.id}>

                            <td>{student.username}</td>

                            <td>{student.email}</td>

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
                    </tr>
                </thead>

                <tbody>

                    {data.etudiants_premium.map(student => (

                        <tr key={student.id}>

                            <td>{student.username}</td>

                            <td>{student.email}</td>

                            <td>{student.superviseur || "-"}</td>

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