package usersServer;

import java.net.*;
import javax.net.ServerSocketFactory;
import javax.net.ssl.*;
import org.bouncycastle.jce.provider.BouncyCastleProvider;
import java.io.*;
import java.security.cert.CertificateFactory;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.nio.charset.StandardCharsets;
import java.security.*;


public class UsersServer2 {

	private static String URL = "jdbc:mysql://localhost:3306/TED";
	private static final String USER = "dba";
	private static final String PASSWORD = "dba";

	private static final int ID_LOGIN = 0;
	private static final int ID_REGISTRO = 1;
	
	public static void main(String[] arstring){

		SSLContext ctx;
		KeyManagerFactory kmf;
		KeyStore ks;

		Socket socket =null;
		SSLSocket sslsocket = null;
		ServerSocket serverSocket= null;

		int SR_port= 5220;
		
		System.out.println("\n\n");
		System.out.println("|--------------------------------------------------------------|");
		System.out.println("|                                                              |");
		System.out.println("|              SERVER USERS PORT 5220                          |");
		System.out.println("|                                                              |");
		System.out.println("|--------------------------------------------------------------|");
		System.out.println("\n");
		

		while (true){

			try {

				Security.addProvider(new BouncyCastleProvider());  // Cargar el provider BC


				String NameStoreKey= "cert_user.p12";
				String PassStore= "";

				char[] fraseclave = PassStore.toCharArray();

				ks = KeyStore.getInstance("PKCS12");
				ks.load(new FileInputStream(NameStoreKey), fraseclave);

				kmf = KeyManagerFactory.getInstance("SunX509");
				kmf.init(ks, fraseclave);
				
				ctx = SSLContext.getInstance("TLS");
				ctx.init(kmf.getKeyManagers(),null, null);

				ServerSocketFactory ssf = ServerSocketFactory.getDefault();
				serverSocket = ssf.createServerSocket(SR_port);

				System.out.println("Servidor escuchando en puerto: "+SR_port);

				socket = serverSocket.accept();

				System.out.println("Cliente conectado desde: "+socket.getRemoteSocketAddress());

				
				SSLSocketFactory sslSf = ctx.getSocketFactory();

				//Actualizamos el socketm para que ahora sea ssl
				sslsocket = (SSLSocket)  sslSf.createSocket(socket, null,   socket.getPort(), false);
				// el modo de usar el soclet debe de ser servidor
				sslsocket.setUseClientMode(false);

				System.out.println("CONVERT TO SECURE SOCKET TLS  ....... \n");

				OutputStream Flujo_salida2 = sslsocket.getOutputStream();
				InputStream Flujo_entrada2 = sslsocket.getInputStream();

				DataOutputStream Flujo_s2= new DataOutputStream(Flujo_salida2);
				DataInputStream Flujo_e2 = new DataInputStream(Flujo_entrada2);

				int id_peticion = Flujo_e2.readInt();

				if (id_peticion == ID_LOGIN) {
					
					System.out.println("Peticion de Login recibida");
					
					int numberToSign = (int) (Math.random() * Integer.MAX_VALUE);
					System.out.println("Numero aleatorio que debe firmar el cliente: "+numberToSign);
					Flujo_s2.writeInt(numberToSign);

					long long_req = Flujo_e2.readLong();	
					Flujo_s2.writeLong(long_req);


					// creo espacio para leer fichero
					byte[] buffer_req_SR= new byte[(int) long_req];

					//RECIBIMOS EL FICHERO
					int NumBytesLeidos_SR=0;
					long long_recibida_fich=0;

					FileOutputStream Fichero_req_SR= new FileOutputStream("signature");
					do{
						NumBytesLeidos_SR=Flujo_e2.read(buffer_req_SR);
						long_recibida_fich = long_recibida_fich+NumBytesLeidos_SR;
						Fichero_req_SR.write(buffer_req_SR,0,NumBytesLeidos_SR);
						System.out.println("Recibiendo Fichero ...");
					} while (long_recibida_fich<long_req);
					Fichero_req_SR.close();


					int longitudNameUser = Flujo_e2.readInt();

					Flujo_s2.writeInt(longitudNameUser);

					byte[] nameUserBA= new byte[longitudNameUser];

					Flujo_e2.read(nameUserBA);

					String nameUser = new String(nameUserBA, StandardCharsets.UTF_8);
					System.out.println("Nombre de usuario del cliente: "+nameUser.toString());

					Connection con;
					int userId = -1;
					String pem ="";

					try {
						con = DriverManager.getConnection(URL, USER, PASSWORD);

						PreparedStatement statement =con.prepareStatement("SELECT * from usuarios WHERE  nombre = ?");
						statement.setString(1, nameUser.toString());
						ResultSet rs = statement.executeQuery();

						while(rs.next()) {
							userId= rs.getInt(1);
							pem =rs.getString(3);
						}

						con.close();
					} catch (SQLException e) {
						e.printStackTrace();
					}

					System.out.println("Numero firmado: "+new String(buffer_req_SR, StandardCharsets.UTF_8));

					CertificateFactory cf = CertificateFactory.getInstance("X.509");
					InputStream caInput = new BufferedInputStream(new ByteArrayInputStream(pem.getBytes(StandardCharsets.UTF_8)));
					java.security.cert.Certificate cert = cf.generateCertificate(caInput);

					PublicKey pk= cert.getPublicKey();

					Signature s = Signature.getInstance("SHA512withRSA");
					s.initVerify(pk);
					s.update(String.valueOf(numberToSign).getBytes());

					if(s.verify(buffer_req_SR)) {
						System.out.println("Verificacion de firma correcta");
						System.out.println("Envio identificador al cliente");
						Flujo_s2.writeInt(userId);
					}
					else Flujo_s2.writeInt(-2);




				}else if(id_peticion == ID_REGISTRO) {
					
					System.out.println("Peticion de Registro recibida");
				
					int longitudNameUser = Flujo_e2.readInt();
					Flujo_s2.writeInt(longitudNameUser);
					byte[] nameUserBA= new byte[longitudNameUser];
					Flujo_e2.read(nameUserBA);
					String nameUser = new String(nameUserBA, StandardCharsets.UTF_8);
					System.out.println("Nombre de usuario del cliente: "+nameUser.toString());
					
					int longitudPEM = Flujo_e2.readInt();
					Flujo_s2.writeInt(longitudPEM);
					byte[] pemBA= new byte[longitudPEM];
					Flujo_e2.read(pemBA);
					String pem = new String(pemBA, StandardCharsets.UTF_8);
					System.out.println("Certificado PEM del cliente:\n"+pem.toString());
					
					Connection con;
					int resultado = -1;
					try {
						con = DriverManager.getConnection(URL, USER, PASSWORD);

						PreparedStatement statement =con.prepareStatement("insert into usuarios (nombre, pem) values (?, ?)");
						statement.setString(1, nameUser.toString());
						statement.setString(2, pem.toString());
						statement.execute();

						con.close();
						resultado = 1;
					} catch (SQLException e) {
						e.printStackTrace();
					}
					
					Flujo_s2.writeInt(resultado);
					
					
				}
			
				
				
			
			}catch (Exception e) {
				System.out.println("ERROR CAPTURADO:"+e.toString());
			}


			finally{ 
				try { 
					if (socket != null)  socket.close();
					if (sslsocket != null)  sslsocket.close();
					if (serverSocket != null)  serverSocket.close();
				} 
				catch (IOException io)
				{ 
					System.out.println("ERROR CIERRE SOCKETSSL:"+io.toString());
				} 
			} 
		}
	}
}
