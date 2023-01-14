from django.shortcuts import render
from divulgar.models import Pet,Raca
from .models import PedidoAdocao
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
# Create your views here.
@login_required
def listar_pets(request):
    if request.method == "GET":
        pets = Pet.objects.filter(status="P")
        racas = Raca.objects.all()

        cidade = request.GET.get('cidade')
        raca_filter = request.GET.get('raca')

        if cidade:
            pets = pets.filter(cidade__icontains=cidade)

        if raca_filter is (None or ''):
            raca_filter = racas
        elif raca_filter:
             pets = pets.filter(raca__id=raca_filter)
             raca_filter = Raca.objects.get(id=raca_filter)

        
        return render(request, 'listar_pets.html', {'pets': pets, 'racas': racas, 'cidade': cidade, 'raca_filter': raca_filter})

@login_required
def pedido_adocao(request, id_pet):
    pet = Pet.objects.filter(id=id_pet).filter(status="P")

    if not pet.exists():
        messages.add_message(request, constants.ERROR, 'Pedido de adoção falhou, o id desse pet não existe ou o mesmo não esta mais para adoção!')
        return redirect('/adotar')
    
    #TODO same user can't make more than one request per pet

    pedido = PedidoAdocao(pet=pet.first(),
                          usuario=request.user,
                          data=datetime.now())

    pedido.save()

    messages.add_message(request, constants.SUCCESS, 'Pedido de adoção realizado, você receberá um e-mail caso ele seja aprovado.')
    return redirect('/adotar')

@login_required
def processa_pedido_adocao(request, id_pedido):
    status = request.GET.get('status')
    pedido = PedidoAdocao.objects.get(id=id_pedido)

    #TODO check if pedido id exists and check if this id was already refused or approved and check if the user is the owner

    if status == "A":
        pedido.status = 'AP'
        string = '''Olá, sua adoção foi aprovada. ...'''
    elif status == "R":
        string = '''Olá, sua adoção foi recusada. ...'''
        pedido.status = 'R'
    else:
        messages.add_message(request, constants.ERROR, 'Erro no processamento do pedido, confirme os dados!')
        return redirect('/divulgar/ver_pedido_adocao')


    pedido.save()

    #TODO alter pet status
    
    print(pedido.usuario.email)
    email = send_mail(
        'Sua adoção foi processada',
        string,
        'vini@genericmail.com',
        [pedido.usuario.email,],
    )
    
    messages.add_message(request, constants.SUCCESS, 'Pedido de adoção processado com sucesso')
    return redirect('/divulgar/ver_pedido_adocao')