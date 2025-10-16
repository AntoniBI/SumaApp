<?php
header('Content-Type: application/json');

$servername = "localhost";
$database = "sumalberic";
$username = "root";
$password = "";


//Create connection
$conn = mysqli_connect($servername,$username,$password,$database);

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $id_usuario = isset($_POST['js-idusuario']) ? htmlspecialchars($_POST['js-idusuario']) : 0;
    $usuario = isset($_POST['js-usuario']) ? htmlspecialchars($_POST['js-usuario']) : '';
    $nombre = isset($_POST['js-nombre']) ? htmlspecialchars($_POST['js-nombre']) : '';
    $apellidos = isset($_POST['js-apellidos']) ? htmlspecialchars($_POST['js-apellidos']) : '';
    $password = isset($_POST['js-password']) ? htmlspecialchars($_POST['js-password']) : '';
    $administrador = isset($_POST['js-administrador']) ? htmlspecialchars($_POST['js-administrador']) : 'false';
    $iprincipal = isset($_POST['js-iprincipal']) ? htmlspecialchars($_POST['js-iprincipal']) : '';
    $isecondary = isset($_POST['js-isecondary']) ? htmlspecialchars($_POST['js-isecondary']) : '';
}

if($id_usuario > 0) {
    $query = 
        "UPDATE usuarios 
        SET usuario = '". $usuario ."'
            ,nombre = '". $nombre ."'
            ,apellidos = '". $apellidos ."'
            ,administrador = ". $administrador ."
            ,id_instrumento_p = ". $iprincipal ."
            ,id_instrumento_s = ". $isecondary ."
            ,fecha_act = current_timestamp()
        WHERE id_usuario = ". $id_usuario;
} else {
    $query = 
        "INSERT INTO usuarios (usuario,nombre,apellidos,password,administrador,id_instrumento_p,id_instrumento_s) 
        VALUES ('". $usuario ."','". $nombre ."','". $apellidos ."','". $password ."',". $administrador .",". $iprincipal .",". $isecondary .")";
}

//echo $query;
$result = mysqli_query($conn,$query);
//sleep(1000);

?>