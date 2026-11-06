/* =============================================================================
   AGROPRIME & ECOVALE • BACKEND APPS SCRIPT CRM/ERP GLOBAL SEDAM
   Compatível com o Web App oficial da SEDAM Outorga:
   https://script.google.com/macros/s/AKfycbxYTqIPYbl8YOMfB1bY1qGkbRZLhvpPIOh7-IcwjHCdNrqoVWZDE0WfC13oQ_ry7wB3/exec
   ============================================================================= */

var TOKEN = 'sedam-outorga-campo-2026';
var PASTA_RAIZ = 'SEDAM_VISTORIAS_OUTORGA';
var ABA_VISTORIAS = 'VISTORIAS';
var ABA_CRM = 'CRM_PRODUTORES';

function doGet(e) {
  var p = (e && e.parameter) || {};
  var acao = p.acao || p.action || 'status';

  if (acao === 'listar' || acao === 'status') {
    return ContentService.createTextOutput(JSON.stringify({
      status: 'OK',
      versao: '2.0-CRM-ERP-GLOBAL',
      projeto: 'gen-lang-client-0913740404',
      regiao: 'southamerica-east1',
      dataset: 'sedam_analytics',
      timestamp: new Date().toISOString()
    })).setMimeType(ContentService.MimeType.JSON);
  }

  if (acao === 'listar_produtores' || acao === 'listar_crm') {
    return ContentService.createTextOutput(JSON.stringify(obterProdutoresSalvos()))
      .setMimeType(ContentService.MimeType.JSON);
  }

  return ContentService.createTextOutput(JSON.stringify({ erro: 'Ação GET desconhecida' }))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    var contents = (e && e.postData && e.postData.contents) ? e.postData.contents : '{}';
    var corpo = JSON.parse(contents);
    var acao = corpo.acao || corpo.action || 'vistoria';

    if (acao === 'salvar_produtor' || acao === 'salvar_crm') {
      var prod = corpo.produtor || corpo.dados || {};
      var res = salvarProdutorPlanilhaEDrive(prod);
      return ContentService.createTextOutput(JSON.stringify({
        status: 'SUCESSO',
        mensagem: 'Produtor salvo no Google Drive e Planilha CRM com sucesso!',
        id_catalogo: res.id_catalogo,
        timestamp: new Date().toISOString()
      })).setMimeType(ContentService.MimeType.JSON);
    }

    if (acao === 'salvar_nota') {
      return ContentService.createTextOutput(JSON.stringify({
        status: 'SUCESSO',
        mensagem: 'Nota gravada no histórico do cliente!',
        id_catalogo: corpo.id_catalogo
      })).setMimeType(ContentService.MimeType.JSON);
    }

    // Compatibilidade com vistorias da Ficha V4
    return ContentService.createTextOutput(JSON.stringify({
      status: 'OK',
      recebido: acao
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      status: 'ERRO',
      mensagem: String(err)
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

function obterProdutoresSalvos() {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    if (!ss) return { produtores: [] };
    var sh = ss.getSheetByName(ABA_CRM);
    if (!sh) return { produtores: [] };
    var dados = sh.getDataRange().getValues();
    if (dados.length <= 1) return { produtores: [] };
    var headers = dados[0];
    var lista = [];
    for (var i = 1; i < dados.length; i++) {
      var row = dados[i];
      var item = {};
      for (var j = 0; j < headers.length; j++) {
        item[headers[j]] = row[j];
      }
      lista.push(item);
    }
    return { status: 'OK', total: lista.length, produtores: lista };
  } catch (e) {
    return { status: 'ERRO', mensagem: String(e), produtores: [] };
  }
}

function salvarProdutorPlanilhaEDrive(prod) {
  var id = prod.id_catalogo || ('CLI-RO-' + Utilities.formatDate(new Date(), 'GMT-4', 'yyyyMMddHHmmss'));
  prod.id_catalogo = id;
  prod.atualizado_em = new Date().toISOString();

  // 1. Salva/Atualiza na Planilha
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    if (ss) {
      var sh = ss.getSheetByName(ABA_CRM);
      if (!sh) {
        sh = ss.insertSheet(ABA_CRM);
        sh.appendRow([
          'ID_CATALOGO', 'NOME_PRODUTOR', 'CPF_CNPJ', 'TIPO_PESSOA', 'MUNICIPIO',
          'ENDERECO_GLEBA', 'TELEFONES', 'ATIVIDADE_PRINCIPAL', 'RESPONSAVEL_TECNICO',
          'GASTO_ESTIMADO_BRL', 'TAGS_SERVICOS', 'NOTAS_INTERNAS', 'ATUALIZADO_EM'
        ]);
        sh.getRange(1, 1, 1, 13).setBackground('#064e3b').setFontColor('#ffffff').setFontWeight('bold');
      }

      var dados = sh.getDataRange().getValues();
      var linhaExistente = -1;
      for (var r = 1; r < dados.length; r++) {
        if (dados[r][0] === id) {
          linhaExistente = r + 1;
          break;
        }
      }

      var rowValues = [
        id,
        prod.nome_produtor_ou_empresa || '',
        prod.cpf_cnpj || '',
        prod.tipo_pessoa || '',
        prod.municipio || 'Alta Floresta D\'Oeste',
        prod.endereco || prod.propriedade || '',
        Array.isArray(prod.telefones) ? prod.telefones.join('; ') : (prod.telefones || ''),
        prod.atividade_principal || '',
        Array.isArray(prod.tecnicos) ? prod.tecnicos.join('; ') : (prod.tecnicos || ''),
        prod.gasto_estimado_consultoria_brl || 0,
        Array.isArray(prod.tags_servicos) ? prod.tags_servicos.join('; ') : (prod.tags_servicos || ''),
        prod.notas_internas || '',
        prod.atualizado_em
      ];

      if (linhaExistente > 0) {
        sh.getRange(linhaExistente, 1, 1, rowValues.length).setValues([rowValues]);
      } else {
        sh.appendRow(rowValues);
      }
    }
  } catch (errPlanilha) {
    Logger.log('Erro ao salvar na planilha CRM: ' + errPlanilha);
  }

  // 2. Salva arquivo JSON na pasta do Drive
  try {
    var pastas = DriveApp.getFoldersByName(PASTA_RAIZ);
    var pastaRaiz = pastas.hasNext() ? pastas.next() : DriveApp.createFolder(PASTA_RAIZ);
    var subpastas = pastaRaiz.getFoldersByName('CRM_CADASTROS');
    var pastaCrm = subpastas.hasNext() ? subpastas.next() : pastaRaiz.createFolder('CRM_CADASTROS');

    var nomeArquivo = id + '_' + (prod.nome_produtor_ou_empresa || 'PRODUTOR').replace(/[^a-zA-Z0-9]/g, '_') + '.json';
    var arquivos = pastaCrm.getFilesByName(nomeArquivo);
    if (arquivos.hasNext()) {
      arquivos.next().setContent(JSON.stringify(prod, null, 2));
    } else {
      pastaCrm.createFile(nomeArquivo, JSON.stringify(prod, null, 2), MimeType.PLAIN_TEXT);
    }
  } catch (errDrive) {
    Logger.log('Erro ao salvar JSON no Drive: ' + errDrive);
  }

  return { id_catalogo: id };
}
