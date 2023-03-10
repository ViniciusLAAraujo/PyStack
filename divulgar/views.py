from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Tag,Raca,Pet
from django.contrib import messages
from django.contrib.messages import constants
from django.shortcuts import redirect
from adotar.models import PedidoAdocao
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
# Create your views here.

@login_required
def novo_pet(request):
    tags = Tag.objects.all()
    racas = Raca.objects.all()
    if request.method == "GET":
        return render(request, 'novo_pet.html',{'tags':tags,'racas':racas})
    elif request.method == "POST":
        foto = request.FILES.get('foto')
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        estado = request.POST.get('estado')
        cidade = request.POST.get('cidade')
        telefone = request.POST.get('telefone')
        tags_selec = request.POST.getlist('tags')
        raca = request.POST.get('raca')

        if len(nome.strip()) == 0 or len(descricao.strip()) == 0 or len(estado.strip()) == 0 or len(telefone.strip()) == 0 or (raca is None) or len(tags_selec)==0 or (foto is None):
            messages.add_message(request,constants.ERROR,'Fill all camps!')
            return redirect('/divulgar/novo_pet')

        valid_raca = racas.filter(id=raca)
        if not valid_raca:
            messages.add_message(request,constants.ERROR,'This is not a valid race!')
            return redirect('/divulgar/novo_pet')

        for tag_id in tags_selec:
            tag = tags.filter(id=tag_id)
            if not tag:
                messages.add_message(request,constants.ERROR,'There is at least one not a valid tag!')
                return redirect('/divulgar/novo_pet')

        pet = Pet(
            usuario=request.user,
            foto=foto,
            nome=nome,
            descricao=descricao,
            estado=estado,
            cidade=cidade,
            telefone=telefone,
            raca_id=raca,
        )

        pet.save()
        
        for tag_id in tags_selec:
            tag = Tag.objects.get(id=tag_id)
            pet.tags.add(tag)

        pet.save()

        messages.add_message(request, constants.SUCCESS, 'New pet has been register')
        return render(request, 'novo_pet.html', {'tags': tags, 'racas': racas})

@login_required
def seus_pets(request):
    if request.method == "GET":
        pets = Pet.objects.filter(usuario=request.user)
        return render(request, 'seus_pets.html', {'pets': pets})

@login_required
def remover_pet(request, id):
    pet = Pet.objects.get(id=id)

    if not pet.usuario == request.user:
        messages.add_message(request, constants.ERROR, 'This pet is not yours!')
        return redirect('/divulgar/seus_pets')

    pet.delete()
    messages.add_message(request, constants.SUCCESS, 'Removed with success.')
    return redirect('/divulgar/seus_pets')

@login_required
def ver_pet(request, id):
    if request.method == "GET":
        pet = Pet.objects.get(id = id)
        return render(request, 'ver_pet.html', {'pet': pet})

@login_required
def ver_pedido_adocao(request):
    if request.method == "GET":
        pedidos = PedidoAdocao.objects.filter(usuario=request.user).filter(status="AG")
        return render(request, 'ver_pedido_adocao.html', {'pedidos': pedidos})

@login_required
def dashboard(request):
    if request.method == "GET":
        return render(request, 'dashboard.html')

@login_required
@csrf_exempt 
def api_adocoes_por_raca(request):
    racas = Raca.objects.all()

    qtd_adocoes = []
    for raca in racas:
        adocoes = PedidoAdocao.objects.filter(pet__raca=raca).count() #TODO add filter for approved adoptions and non approved ones
        qtd_adocoes.append(adocoes)

    racas = [raca.raca for raca in racas]
    data = {'qtd_adocoes': qtd_adocoes,
            'labels': racas}

    return JsonResponse(data)