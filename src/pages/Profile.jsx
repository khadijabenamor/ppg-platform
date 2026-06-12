import { useEffect, useState } from "react";
import { getProfile, updateProfile , changePassword } from "../api/profile";

export default function Profile() {

  const token = localStorage.getItem("access_token");
  const [avatarPreview, setAvatarPreview] = useState(null);
  const [form, setForm] = useState({
    username: "",
    first_name: "",
    last_name: "",
    email: "",
  });

  const [passwordData, setPasswordData] = useState({
    old_password: "",
    new_password: "",
    confirm_password: "",
  });
  const [message, setMessage] = useState("");

  const [avatar, setAvatar] = useState(null);
  const [avatarUrl, setAvatarUrl] = useState(null);
  {/*const [avatarUrl, setAvatarUrl] = useState("");*/}

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const res = await getProfile(token);

      setForm({
        username: res.data.username || "",
        first_name: res.data.first_name || "",
        last_name: res.data.last_name || "",
        email: res.data.email || "",
      });
      if (res.data.avatar_url) {
  setAvatarPreview(res.data.avatar_url);
}
      setAvatarUrl(res.data.avatar_url);
    } catch (err) {
      console.error(err);
    }
  };

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };
  const handlePasswordChange = (e) => {
  setPasswordData({
    ...passwordData,
    [e.target.name]: e.target.value,
  });
};
  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      {/*await updateProfile(token, form);*/}
      const formData = new FormData();

      formData.append("username", form.username);
      formData.append("first_name",form.first_name);
      formData.append("last_name",form.last_name);
      formData.append("email",form.email);
      if (avatar) {
          formData.append("avatar",avatar);
      }
      await updateProfile(token,formData);

      setMessage("Profil mis à jour avec succès");
    } catch (err) {
      setMessage("Erreur lors de la mise à jour");
    }
  };
  const handlePasswordSubmit = async (e) => {

  e.preventDefault();

  if (
    passwordData.new_password !==
    passwordData.confirm_password
  ) {
    setMessage(
      "Les mots de passe ne correspondent pas"
    );
    return;
  }

  try {

    const res =
      await changePassword(
        token,
        passwordData.old_password,
        passwordData.new_password
      );

    setMessage(
      res.data.message
    );

    setPasswordData({
      old_password: "",
      new_password: "",
      confirm_password: "",
    });

  } catch (err) {

    setMessage(
      err.response?.data?.error ||
      "Erreur"
    );

  }
};

  return (
    <div style={{
      maxWidth: "750px",
      margin: "50px auto",
      padding: "35px",
      background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: "20px",
    boxShadow: "0 10px 30px rgba(0,0,0,0.15)"
    }}>
    {/*{avatarUrl && (
  <img
    src={avatarUrl}
    alt="avatar"
    style={{
      width: "120px",
      height: "120px",
      borderRadius: "50%",
      objectFit: "cover",
      display: "block",
      marginBottom: "20px"
    }}
  />
)}*/}
<div
  style={{
    display: "flex",
    justifyContent: "center",
    marginBottom: "20px"
  }}
>
  <img
    src={
      avatarPreview ||
      "https://via.placeholder.com/150"
    }
    alt="Avatar"
    style={{
      width: "140px",
      height: "140px",
      borderRadius: "50%",
      objectFit: "cover",
      border: "4px solid var(--accent)",
      boxShadow: "0 8px 20px rgba(0,0,0,0.2)"
    }}
  />
</div>


      <h1 style={{
    marginBottom: "30px",
    fontSize: "32px",
    fontFamily: "Syne",
    fontWeight: "800"
  }}>Mon Profile</h1>

      <form onSubmit={handleSubmit}>

        <div style={{ marginBottom: "20px" }}>
          <label   style={{
      display: "block",
      marginBottom: "8px",
      fontWeight: "600",
      color: "var(--text)"
    }} >Nom d'utilisateur</label>
          <input
            name="username"
            value={form.username}
            onChange={handleChange}
            style={{
      width: "100%",
      padding: "12px 16px",
      borderRadius: "10px",
      border: "1px solid var(--border)",
      background: "var(--surface)",
      color: "var(--text)",
      fontSize: "15px"
    }}
          />
        </div>

        <div style={{ marginBottom: "20px" }}>
          <label style={{
      display: "block",
      marginBottom: "8px",
      fontWeight: "600",
      color: "var(--text)"
    }}>Prénom</label>
          <input
            name="first_name"
            value={form.first_name}
            onChange={handleChange}
            style={{
      width: "100%",
      padding: "12px 16px",
      borderRadius: "10px",
      border: "1px solid var(--border)",
      background: "var(--surface)",
      color: "var(--text)",
      fontSize: "15px"
    }}
          />
        </div>

        <div style={{ marginBottom: "20px" }}>
          <label style={{
      display: "block",
      marginBottom: "8px",
      fontWeight: "600",
      color: "var(--text)"
    }}>Nom</label>
          <input
            name="last_name"
            value={form.last_name}
            onChange={handleChange}
            style={{
      width: "100%",
      padding: "12px 16px",
      borderRadius: "10px",
      border: "1px solid var(--border)",
      background: "var(--surface)",
      color: "var(--text)",
      fontSize: "15px"
    }}
          />
        </div>

        <div style={{ marginBottom: "20px" }}>
          <label style={{
      display: "block",
      marginBottom: "8px",
      fontWeight: "600",
      color: "var(--text)"
    }}>Email</label>
          <input
            name="email"
            value={form.email}
            onChange={handleChange}
            style={{
      width: "100%",
      padding: "12px 16px",
      borderRadius: "10px",
      border: "1px solid var(--border)",
      background: "var(--surface)",
      color: "var(--text)",
      fontSize: "15px"
    }}
          />
        </div>



     {/*   <div>
  <label>Photo de profil</label>
   
  <input
    type="file"
    accept="image/*"
    onChange={(e) =>
      setAvatar(
        e.target.files[0]
      )
    }
  />
</div>*/}
<div style={{ marginBottom: "25px" }}>

  <label
    style={{
      display: "block",
      marginBottom: "10px",
      fontWeight: "600"
    }}
  >
    📷 Photo de profil
  </label>

  <div
    onClick={() =>
      document
        .getElementById("avatarInput")
        .click()
    }
    style={{
      border: "2px dashed var(--accent)",
      borderRadius: "15px",
      padding: "25px",
      textAlign: "center",
      cursor: "pointer",
      background: "var(--surface)"
    }}
  >
    {avatar ? (
      <div>
        <strong>{avatar.name}</strong>
      </div>
    ) : (
      <div>
        Cliquez ici pour sélectionner une image
      </div>
    )}
  </div>

  <input
    id="avatarInput"
    type="file"
    accept="image/*"
    style={{ display: "none" }}
    onChange={(e) => {
      const file = e.target.files[0];

      if (file) {

        setAvatar(file);

        setAvatarPreview(
          URL.createObjectURL(file)
        );
      }
    }}
  />

</div>
{avatarPreview && (
  <button
    type="button"
    onClick={() => {
      setAvatar(null);
      setAvatarPreview(null);
    }}
    style={{
      marginTop: "10px",
      background: "transparent",
      border: "none",
      color: "#ff6584",
      cursor: "pointer",
      fontWeight: "600"
    }}
  >
    🗑 Supprimer la photo
  </button>
)}
          
        <button type="submit"   type="submit"
  style={{
    width: "100%",
    padding: "14px",
    border: "none",
    borderRadius: "12px",
    background:
      "linear-gradient(135deg, var(--accent), var(--accent2))",
    color: "#fff",
    fontSize: "16px",
    fontWeight: "700",
    cursor: "pointer",
    marginTop: "15px"
  }}>
          Sauvegarder
        </button>

      </form>
      <br></br>
      <hr />
      <br></br>
      <h2>Changer le mot de passe</h2>
      <br></br>
      <form onSubmit={handlePasswordSubmit}>

  <div style={{ marginBottom: "20px" }}>
    <label style={{
      display: "block",
      marginBottom: "8px",
      fontWeight: "600",
      color: "var(--text)"
    }}>Ancien mot de passe</label>
    <input
      type="password"
      name="old_password"
      value={passwordData.old_password}
      onChange={handlePasswordChange}
      style={{
      width: "100%",
      padding: "12px 16px",
      borderRadius: "10px",
      border: "1px solid var(--border)",
      background: "var(--surface)",
      color: "var(--text)",
      fontSize: "15px"
    }}
    />
  </div>

  <div style={{ marginBottom: "20px" }}>
    <label style={{
      display: "block",
      marginBottom: "8px",
      fontWeight: "600",
      color: "var(--text)"
    }}>Nouveau mot de passe</label>
    <input
      type="password"
      name="new_password"
      value={passwordData.new_password}
      onChange={handlePasswordChange}
      style={{
      width: "100%",
      padding: "12px 16px",
      borderRadius: "10px",
      border: "1px solid var(--border)",
      background: "var(--surface)",
      color: "var(--text)",
      fontSize: "15px"
    }}
    />
  </div>

  <div style={{ marginBottom: "20px" }}>
    <label style={{
      display: "block",
      marginBottom: "8px",
      fontWeight: "600",
      color: "var(--text)"
    }}>Confirmer le mot de passe</label>
    <input
      type="password"
      name="confirm_password"
      value={passwordData.confirm_password}
      onChange={handlePasswordChange}
      style={{
      width: "100%",
      padding: "12px 16px",
      borderRadius: "10px",
      border: "1px solid var(--border)",
      background: "var(--surface)",
      color: "var(--text)",
      fontSize: "15px"
    }}
    />
  </div>

  <button type="submit"  style={{
    width: "100%",
    padding: "14px",
    border: "none",
    borderRadius: "12px",
    background:
      "linear-gradient(135deg, #f7971e, #ffd200)",
    color: "#000",
    fontSize: "16px",
    fontWeight: "700",
    cursor: "pointer",
    marginTop: "15px"
  }}>
    Modifier le mot de passe
  </button>

</form>

      {message && (
        <div
    style={{
      marginTop: "20px",
      padding: "12px",
      borderRadius: "10px",
      background: "rgba(67,233,123,0.1)",
      border: "1px solid rgba(67,233,123,0.3)",
      color: "#43e97b",
      textAlign: "center",
      fontWeight: "600"
    }}
  >
        <p>{message}</p>
        </div>
      )}

    </div>
  );
}